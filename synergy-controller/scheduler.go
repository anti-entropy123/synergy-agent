package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

const FORCEADJUSTOP = "FORCEADJUST"

var (
	// nodeIPs = []string{"localhost"}
	nodeIPs = []string{}   // 所有节点
	mutex   = sync.Mutex{} // 保护共享数据

	// 节点状态锁
	statusMutex = sync.Mutex{}
	statusMap   = make(map[string]NodeStatus)

	// 标记一个周期内, 是否有对应类型的函数到达过.
	shortFlag = false
	longFlag  = false

	// 每隔若干个函数请求, 通过channel通知Monitor更新状态.
	flushStChan    chan bool = make(chan bool, 1)
	flushThreshold           = 64

	// 标记预先分区调整.
	forceAdjustLock sync.Mutex
	forceAdjust     []ForceAdjustCommand = make([]ForceAdjustCommand, 0, 1)
)

type ForceAdjustCommand struct {
	partition string
	nums      int
}

type SelectFunc = func(map[string]NodeStatus, Task) (string, NodeStatus)

const (
	dispatchPeriod = 100 * time.Millisecond
	waitCompPeriod = 2 * time.Second
	flushStPeriod  = 1 * time.Second
)

// 节点状态结构体
type NodeStatus struct {
	Timestamp int64   `json:"timestamp"`
	CPUUsage  float64 `json:"cpu_usage"`
	// MemUsage  float64 `json:"mem_usage"`
	Policy string `json:"policy"`
	Node   string `json:"node"`
}

// 任务结构体
type Task struct {
	Name     string
	Script   string
	Param    int
	Unused1  int
	Seq      int
	ConStart string
}

func updateForceAdjust(commd ForceAdjustCommand) {
	fmt.Println("updateForceAdjust")
	forceAdjustLock.Lock()
	defer forceAdjustLock.Unlock()

	if len(forceAdjust) == 0 {
		forceAdjust = append(forceAdjust, commd)
	} else {
		fmt.Printf("old command %v will be replace by new %v", forceAdjust[0], commd)
		forceAdjust[0] = commd
	}
}

// 读取 `test` 文件并解析任务
func ReadTasksFromFile(filename string) []Task {
	var tasks []Task
	file, err := os.Open(filename)
	if err != nil {
		fmt.Printf("无法打开文件 %s: %v\n", filename, err)
		return tasks
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	conStart := time.Now()
	timeStr := conStart.Format("2006-01-02 15:04:05.000")

	for scanner.Scan() {
		line := scanner.Text()
		fields := strings.Fields(line)

		task_name := fields[0]
		script := fields[1]
		param, _ := strconv.Atoi(fields[2])

		if len(fields) < 3 {
			log.Fatalf("Wrong trace item: %s\n", line)
		}

		if task_name == FORCEADJUSTOP {
			tasks = append(tasks, Task{task_name, script, param, 0, 0, ""})
			continue
		}

		unused1, _ := strconv.Atoi(fields[3])
		seq, _ := strconv.Atoi(fields[4])

		task := Task{
			Name:     task_name,
			Script:   script,
			Param:    param,
			Unused1:  unused1,
			Seq:      seq,
			ConStart: timeStr,
		}
		tasks = append(tasks, task)
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("读取文件时出错: %v\n", err)
	}
	return tasks
}

// 从本地的缓存中, 获取所有节点状态.
// func GetNodeStatuses() map[string]NodeStatus {
// 	return statusMap
// }

func UpdateNodeStatus() {
	statusMutex.Lock()
	defer statusMutex.Unlock()

	newStatusMap := make(map[string]NodeStatus)

	var wg sync.WaitGroup
	var mutex sync.Mutex
	for _, ip := range nodeIPs {
		wg.Add(1)
		go func(ip string) {
			defer wg.Done()
			url := fmt.Sprintf("http://%s:20251/get_status", ip)
			resp, err := http.Get(url)
			if err != nil {
				fmt.Printf("获取节点 %s 状态失败: %v\n", ip, err)
				return
			}
			defer resp.Body.Close()

			var statuses []NodeStatus
			body, _ := io.ReadAll(resp.Body)
			json.Unmarshal(body, &statuses)

			if len(statuses) > 0 {
				mutex.Lock()
				newStatusMap[ip] = statuses[len(statuses)-1] // 取最新状态
				mutex.Unlock()
			}
		}(ip)
	}
	wg.Wait()

	statusMap = newStatusMap

	// 记录系统当前节点状态日志
	fmt.Println("\n==== 当前系统节点状态 ====")
	fifoNodes, cfsNodes := 0, 0
	for _, ip := range nodeIPs {
		status := statusMap[ip]
		fmt.Printf("节点 %s | 调度策略: %s | CPU 利用率: %.2f%%\n", ip, status.Policy, status.CPUUsage)
		if status.Policy == "f" {
			fifoNodes++
		} else {
			cfsNodes++
		}
	}
	fmt.Printf("FIFO 分区节点数: %d, CFS 分区节点数: %d\n", fifoNodes, cfsNodes)

}

func isLongTask(task *Task) bool {
	return task.Param >= 31
}

// 统计任务类型
func CountTasks(tasks []Task) (int, int) {
	shortTasks, longTasks := 0, 0
	for _, task := range tasks {
		if task.Name == FORCEADJUSTOP {
			continue
		}

		if isLongTask(&task) {
			longTasks++
		} else {
			shortTasks++
		}
	}
	return shortTasks, longTasks
}

func LeastLoaded(nodes map[string]NodeStatus, task Task) (string, NodeStatus) {
	var selectedNode string
	var selectedStatus NodeStatus

	minLoad := 100.0
	for ip, status := range nodes {
		if status.CPUUsage < minLoad {
			minLoad = status.CPUUsage
			selectedNode = ip
			selectedStatus = status
		}
	}

	return selectedNode, selectedStatus
}

func RandomNode(nodes map[string]NodeStatus, task Task) (string, NodeStatus) {
	for ip, status := range nodes {
		return ip, status
	}

	return "", NodeStatus{}
}

func HashNode(nodes map[string]NodeStatus, task Task) (string, NodeStatus) {
	if len(nodes) == 0 {
		return "", NodeStatus{}
	}

	ips := []string{}
	statuses := []*NodeStatus{}

	for _, ip := range nodeIPs {
		if status, exist := nodes[ip]; exist {
			ips = append(ips, ip)
			statuses = append(statuses, &status)
		}
	}

	key := task.Seq % len(ips)
	return ips[key], *statuses[key]
}

// 根据任务类型 (长/短) 选择最低负载的合适节点
func SelectBestNode(statusMap map[string]NodeStatus, task Task, partition bool, selectBy SelectFunc) string {
	nodes := make(map[string]NodeStatus)

	var policy string = "f"
	if isLongTask(&task) {
		policy = "c"
	}

	for ip, status := range statusMap {
		if status.CPUUsage >= 80 {
			continue
		}
		if partition && status.Policy != policy {
			continue
		}

		nodes[ip] = status
	}

	selectedNode, status := selectBy(nodes, task)

	var taskTypeStr string
	switch policy {
	case "f":
		taskTypeStr = "短任务 (FIFO)"
	case "c":
		taskTypeStr = "长任务 (CFS)"
	}

	if selectedNode != "" {
		fmt.Printf("任务 %s (%s) 分配到节点 %s (CPU 负载: %.2f%%)\n", task.Name, taskTypeStr, selectedNode, status.CPUUsage)
	} else {
		fmt.Printf("没有可用的 %s 节点，任务 %s 等待调度\n", taskTypeStr, task.Name)
	}
	return selectedNode
}

// 发送任务请求到指定节点
func SendTaskToNode(nodeIP string, task Task) {
	url := fmt.Sprintf("http://%s:20251/set_reqs", nodeIP)
	taskData := fmt.Sprintf("%s %s %d %d %d %s", task.Name, task.Script, task.Param, task.Unused1, task.Seq, task.ConStart)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(taskData)))
	req.Header.Set("Content-Type", "text/plain")

	client := &http.Client{}
	go func() {
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("发送任务 %s 到节点 %s 失败: %v\n", task.Name, nodeIP, err)
			return
		}
		defer resp.Body.Close()
		fmt.Printf("任务 %s 已成功发送到节点 %s\n", task.Name, nodeIP)
	}()

}

func doDispatch(task Task, partition bool, selectBy SelectFunc) bool {
	statusMutex.Lock()
	fmt.Println("dispatcher get statusLock")
	defer statusMutex.Unlock()

	nodeIP := SelectBestNode(statusMap, task, partition, selectBy)
	if nodeIP != "" {
		SendTaskToNode(nodeIP, task)
	} else {
		return false
	}

	fmt.Println("dispatcher release statusLock")
	return true
}

// 任务分发逻辑
func DispatchTasks(tasks []Task, partition bool, selectBy SelectFunc) {
	shortTasks, longTasks := CountTasks(tasks)

	fmt.Printf("\n==== 任务统计 ====\n")
	fmt.Printf("收到短任务: %d 个, 长任务: %d 个\n", shortTasks, longTasks)

	flushCnt := 0

	for {
		var nextTasks []Task

		for _, task := range tasks {
			// FORCEADJUST L 3 | FORCEADJUST S 5
			if task.Name == FORCEADJUSTOP {
				script := strings.ToUpper(task.Script)
				if !(script == "L" || script == "S") {
					log.Fatalf("Bad FORCEADJUST COMMAND, partition=%s\n", script)
				}

				commd := ForceAdjustCommand{partition: script, nums: task.Param}
				updateForceAdjust(commd)
				continue
			}

			longTask := isLongTask(&task)

			if longTask {
				flushCnt += 5
			} else {
				flushCnt += 1
			}
			if flushCnt > flushThreshold {
				flushCnt = 0
				flushStChan <- true
			}

			if longTask {
				longFlag = true
			} else {
				shortFlag = true
			}

			if !doDispatch(task, partition, selectBy) {
				nextTasks = append(nextTasks, task)
			}
		}

		fmt.Println("dispatch finish one batch")
		if len(nextTasks) == 0 {
			break
		}
		tasks = nextTasks
		time.Sleep(dispatchPeriod)
	}
}

// 计算分区平均 CPU 负载
func CalculatePartitionLoad(statusMap map[string]NodeStatus) (float64, float64, int, int) {
	var fifoLoad, cfsLoad float64
	var fifoCount, cfsCount int

	for _, status := range statusMap {
		if status.Policy == "f" {
			fifoLoad += status.CPUUsage
			fifoCount++
		} else if status.Policy == "c" {
			cfsLoad += status.CPUUsage
			cfsCount++
		}
	}

	if fifoCount == 0 {
		fifoLoad = 100 // 默认 100% 负载
	} else {
		fifoLoad /= float64(fifoCount)
	}

	if cfsCount == 0 {
		cfsLoad = 100 // 默认 100% 负载
	} else {
		cfsLoad /= float64(cfsCount)
	}

	fmt.Printf("FIFO 分区平均负载: %.2f%%, CFS 分区平均负载: %.2f%%\n", fifoLoad, cfsLoad)

	return fifoLoad, cfsLoad, fifoCount, cfsCount
}

// 选择最低负载节点并等待任务完成后切换策略
func SelectAndConvertNode(statusMap map[string]NodeStatus, fromPolicy, toPolicy string, force bool) {
	minLoad := 100.0
	var selectedNode *NodeStatus = nil
	var selectedIp = ""

	if force {
		selectedIp = nodeIPs[0]
		node := statusMap[selectedIp]
		selectedNode = &node
		minLoad = selectedNode.CPUUsage
	}

	for ip, status := range statusMap {
		if status.Policy == fromPolicy && status.CPUUsage < minLoad {
			minLoad = status.CPUUsage
			selectedNode = &status
			selectedIp = ip
		}
	}

	if selectedIp != "" {
		statusMutex.Lock()
		defer statusMutex.Unlock()

		fmt.Printf("选择节点 %s 进行 %s -> %s 切换, 当前 CPU 负载: %.2f%%\n", selectedIp, fromPolicy, toPolicy, minLoad)
		// WaitForTasksCompletion(selectedIp)
		ChangePolicy(selectedIp, toPolicy)
		// 如果确定要切换某个 node 的 policy, 先更新本地的 status. 避免再向该节点发送错误的任务类型.
		selectedNode.Policy = toPolicy
		statusMap[selectedIp] = *selectedNode
	}
}

// 等待节点任务执行完成
func WaitForTasksCompletion(ip string) {
	for {
		// statusMap := GetNodeStatuses()
		if status, exists := statusMap[ip]; exists && status.CPUUsage < 10.0 {
			fmt.Printf("节点 %s 任务完成, CPU 负载: %.2f%%, 准备切换策略\n", ip, status.CPUUsage)
			return
		}
		time.Sleep(waitCompPeriod) // 每 2 秒检查一次
		UpdateNodeStatus()
	}
}

// 发送调度策略切换请求并同步中心控制器
func ChangePolicy(ip, newPolicy string) {
	url := fmt.Sprintf("http://%s:20251/change_policy", ip)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(newPolicy)))
	req.Header.Set("Content-Type", "text/plain")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("切换节点 %s 策略失败: %v\n", ip, err)
		return
	}
	defer resp.Body.Close()
	fmt.Printf("成功切换节点 %s 调度策略为 %s\n", ip, newPolicy)
}

func checkAndAdjustPartition() {
	fifoLoad, cfsLoad, fifoCount, cfsCount := CalculatePartitionLoad(statusMap)
	fmt.Printf("监控并调整调度策略, FIFO 分区平均负载: %.2f%%, CFS 分区平均负载: %.2f%%\n", fifoLoad, cfsLoad)

	forceAdjustLock.Lock()
	defer forceAdjustLock.Unlock()

	var from, to string
	// fmt.Printf("checkAndAdjustPartition, forceAdjust=%+v\n", forceAdjust)
	if len(forceAdjust) > 0 {
		// fmt.Printf("存在未完成的 forceCommand\n")

		commd := forceAdjust[0]
		target := commd.nums
		current := -1
		if commd.partition == "S" {
			from, to = "c", "f"
			current = fifoCount
		} else /* commd.partition == "L" */ {
			from, to = "f", "c"
			current = cfsCount
		}

		if current > target {
			from, to = to, from
		} else if current == target {
			forceAdjust = forceAdjust[:0]
			return
		}

		fmt.Printf("强制从 %s 向 %s 分区加入节点, 目标节点数: %d.\n", from, to, commd.nums)
		force := true
		SelectAndConvertNode(statusMap, from, to, force)
		return
	}

	// 测不同数据集需要更改一下切换负载，以下负载适用于600-27 20-32
	force := false
	if fifoLoad < 10 && cfsLoad > 20 && longFlag {
		SelectAndConvertNode(statusMap, "f", "c", force)
	} else if cfsLoad < 10 && fifoLoad > 20 && shortFlag {
		SelectAndConvertNode(statusMap, "c", "f", force)
	}
}

// 监控并调整调度策略
func MonitorAndAdjustPolicies(allowAdjust bool) {
	for {
		fmt.Println("Monitor get statusLock")
		UpdateNodeStatus()

		if allowAdjust {
			checkAndAdjustPartition()
		}

		cleared := false
		for !cleared {
			select {
			case <-flushStChan:
			default:
				cleared = true
			}
		}

		fmt.Println("Monitor release statusLock")

		longFlag = false
		shortFlag = false

		select {
		case <-time.NewTimer(time.Second).C:
		case <-flushStChan:
		}
	}
}

func setup_agents(local bool, allowAdjust bool, partition bool, select_by string) {
	if local {
		nodeIPs = []string{"localhost"}
		return
	}

	if partition {
		// if select_by == "hash" || select_by == "random" {
		// 	log.Fatalln("使用 hash 和 random 必须关闭 partition")
		// }
		if allowAdjust {
			nodeIPs = []string{"172.17.0.5", "172.17.0.6", "172.17.0.7", "172.17.0.8"}
		} else {
			nodeIPs = []string{"172.17.0.9", "172.17.0.10", "172.17.0.11", "172.17.0.12"}
		}
		return
	}

	if allowAdjust {
		log.Fatalln("使用 --allowAdjust 必须开启 --partition")
	}

	nodeIPs = []string{"172.17.0.13", "172.17.0.14", "172.17.0.15", "172.17.0.16"}
}

func main() {
	allowAdjust := false
	local := false
	trace_name := ""
	select_by := ""
	partition := false

	flag.BoolVar(&allowAdjust, "allowAdjust", false, "allow adjust agent policy")
	flag.StringVar(&trace_name, "trace", "test_tiny", "trace file name")
	flag.StringVar(&select_by, "selectBy", "leastLoad", "select node by leastLoad, hash or random")
	flag.BoolVar(&local, "local", false, "use localhost as agent")
	flag.BoolVar(&partition, "partition", false, "partition")
	flag.Parse()

	setup_agents(local, allowAdjust, partition, select_by)

	var selectFunc SelectFunc
	switch select_by {
	case "leastLoad":
		selectFunc = LeastLoaded
	case "random":
		selectFunc = RandomNode
	case "hash":
		selectFunc = HashNode
	default:
		log.Fatalln("wrong selectFunc:", select_by)
	}

	go MonitorAndAdjustPolicies(allowAdjust) // 调度策略监控

	time.Sleep(3 * time.Second)
	traces := ReadTasksFromFile(trace_name)

	// if partition {
	// 	// 对 task 进行排序, 按照 Param 从小到大排序
	// 	for i := 0; i < len(traces); i++ {
	// 		for j := i + 1; j < len(traces); j++ {
	// 			if traces[i].Param > traces[j].Param {
	// 				traces[i], traces[j] = traces[j], traces[i]
	// 			}
	// 		}
	// 	}
	// }

	for _, task := range traces {
		fmt.Print(task.Param, " ")
	}
	fmt.Println()

	DispatchTasks(traces, partition, selectFunc) // 任务分发

	fmt.Println("Dispatch finished.")
	time.Sleep(5 * time.Second)

	// select {}
}
