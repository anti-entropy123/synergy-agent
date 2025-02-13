package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

var (
	nodeIPs = []string{"172.17.0.5", "172.17.0.6", "172.17.0.7", "172.17.0.8"} // 所有节点
	mutex   = sync.Mutex{}                                                     // 保护共享数据

	statusMutex = sync.Mutex{}
	statusMap   = make(map[string]NodeStatus)

	/// 下面两个变量, 标记一个周期内, 是否有对应类型的函数到达过.
	shortFlag = false
	longFlag  = false
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
	Name    string
	Script  string
	Param   int
	Unused1 int
	Unused2 int
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
	for scanner.Scan() {
		fields := strings.Fields(scanner.Text())
		if len(fields) < 5 {
			continue
		}

		param, _ := strconv.Atoi(fields[2])
		unused1, _ := strconv.Atoi(fields[3])
		unused2, _ := strconv.Atoi(fields[4])

		task := Task{
			Name:    fields[0],
			Script:  fields[1],
			Param:   param,
			Unused1: unused1,
			Unused2: unused2,
		}
		tasks = append(tasks, task)
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("读取文件时出错: %v\n", err)
	}
	return tasks
}

// 从本地的缓存中, 获取所有节点状态.
func GetNodeStatuses() map[string]NodeStatus {
	// 记录系统当前节点状态日志
	fmt.Println("\n==== 当前系统节点状态 ====")
	fifoNodes, cfsNodes := 0, 0
	for ip, status := range statusMap {
		fmt.Printf("节点 %s | 调度策略: %s | CPU 利用率: %.2f%%\n", ip, status.Policy, status.CPUUsage)
		if status.Policy == "f" {
			fifoNodes++
		} else {
			cfsNodes++
		}
	}
	fmt.Printf("FIFO 分区节点数: %d, CFS 分区节点数: %d\n", fifoNodes, cfsNodes)

	return statusMap
}

func UpdateNodeStatus() {
	statusMap = make(map[string]NodeStatus)

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
				statusMap[ip] = statuses[len(statuses)-1] // 取最新状态
				mutex.Unlock()
			}
		}(ip)
	}

	wg.Wait()
}

func isLongTask(task *Task) bool {
	return task.Param >= 31
}

// 统计任务类型
func CountTasks(tasks []Task) (int, int) {
	shortTasks, longTasks := 0, 0
	for _, task := range tasks {
		if isLongTask(&task) {
			longTasks++
		} else {
			shortTasks++
		}
	}
	return shortTasks, longTasks
}

// 根据任务类型 (长/短) 选择最低负载的合适节点
func SelectBestNode(statusMap map[string]NodeStatus, task Task, longTask bool) string {
	var selectedNode string
	minLoad := 100.0

	for ip, status := range statusMap {
		if (!longTask && status.Policy == "f") || (longTask && status.Policy == "c") {
			if status.CPUUsage < minLoad {
				minLoad = status.CPUUsage
				selectedNode = ip
			}
		}
	}

	taskTypeStr := "短任务 (FIFO)"
	if longTask {
		taskTypeStr = "长任务 (CFS)"
	}

	if selectedNode != "" {
		fmt.Printf("任务 %s (%s) 分配到节点 %s (CPU 负载: %.2f%%)\n", task.Name, taskTypeStr, selectedNode, minLoad)
	} else {
		fmt.Printf("没有可用的 %s 节点，任务 %s 等待调度\n", taskTypeStr, task.Name)
	}
	return selectedNode
}

// 发送任务请求到指定节点
func SendTaskToNode(nodeIP string, task Task) {
	url := fmt.Sprintf("http://%s:20251/set_reqs", nodeIP)
	taskData := fmt.Sprintf("%s %s %d %d %d", task.Name, task.Script, task.Param, task.Unused1, task.Unused2)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer([]byte(taskData)))
	req.Header.Set("Content-Type", "text/plain")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("发送任务 %s 到节点 %s 失败: %v\n", task.Name, nodeIP, err)
		return
	}
	defer resp.Body.Close()
	fmt.Printf("任务 %s 已成功发送到节点 %s\n", task.Name, nodeIP)
}

// 任务分发逻辑
func DispatchTasks() {
	tasks := ReadTasksFromFile("test")
	shortTasks, longTasks := CountTasks(tasks)

	fmt.Printf("\n==== 任务统计 ====\n")
	fmt.Printf("收到短任务: %d 个, 长任务: %d 个\n", shortTasks, longTasks)

	for {
		var nextTasks []Task

		for _, task := range tasks {
			longTask := isLongTask(&task)
			if longTask {
				longFlag = true
			} else {
				shortFlag = true
			}

			statusMutex.Lock()
			fmt.Println("dispatcher get statusLock")
			statusMap := GetNodeStatuses()
			fmt.Println("dispatcher release statusLock")
			statusMutex.Unlock()

			nodeIP := SelectBestNode(statusMap, task, longTask)
			if nodeIP != "" {
				SendTaskToNode(nodeIP, task)
			} else {
				nextTasks = append(nextTasks, task)
			}
		}

		if len(nextTasks) == 0 {
			break
		}
		tasks = nextTasks
		time.Sleep(1 * time.Second)
	}
}

// 计算分区平均 CPU 负载
func CalculatePartitionLoad(statusMap map[string]NodeStatus) (float64, float64) {
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

	return fifoLoad, cfsLoad
}

// 选择最低负载节点并等待任务完成后切换策略
func SelectAndConvertNode(statusMap map[string]NodeStatus, fromPolicy, toPolicy string) {
	minLoad := 100.0
	var selectedNode *NodeStatus = nil
	var selectedIp = ""

	for ip, status := range statusMap {
		if status.Policy == fromPolicy && status.CPUUsage < minLoad {
			minLoad = status.CPUUsage
			selectedNode = &status
			selectedIp = ip
		}
	}

	if selectedNode != nil {
		fmt.Printf("选择节点 %s 进行 %s -> %s 切换, 当前 CPU 负载: %.2f%%\n", selectedIp, fromPolicy, toPolicy, minLoad)
		WaitForTasksCompletion(selectedIp)
		ChangePolicy(selectedIp, toPolicy)
		// 如果确定要切换某个 node 的 policy, 先更新本地的 status. 避免再向该节点发送错误的任务类型.
		selectedNode.Policy = toPolicy
		statusMap[selectedIp] = *selectedNode
	}
}

// 等待节点任务执行完成
func WaitForTasksCompletion(ip string) {
	for {
		statusMap := GetNodeStatuses()
		if status, exists := statusMap[ip]; exists && status.CPUUsage < 10.0 {
			fmt.Printf("节点 %s 任务完成, CPU 负载: %.2f%%, 准备切换策略\n", ip, status.CPUUsage)
			return
		}
		time.Sleep(1 * time.Second) // 每 2 秒检查一次
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

// 监控并调整调度策略
func MonitorAndAdjustPolicies() {
	for {
		statusMutex.Lock()
		fmt.Println("Monitor get statusLock")
		UpdateNodeStatus()
		statusMap := GetNodeStatuses()

		fifoLoad, cfsLoad := CalculatePartitionLoad(statusMap)
		fmt.Printf("监控并调整调度策略")
		fmt.Printf("FIFO 分区平均负载: %.2f%%, CFS 分区平均负载: %.2f%%\n", fifoLoad, cfsLoad)

		if fifoLoad < 25 && cfsLoad > 75 && longFlag {
			SelectAndConvertNode(statusMap, "f", "c")
		} else if cfsLoad < 25 && fifoLoad > 75 && shortFlag {
			SelectAndConvertNode(statusMap, "c", "f")
		}

		fmt.Println("Monitor release statusLock")
		statusMutex.Unlock()

		longFlag = false
		shortFlag = false

		time.Sleep(1 * time.Second) // 每 5 秒检查一次
	}
}

func main() {
	go MonitorAndAdjustPolicies() // 调度策略监控
	go DispatchTasks()            // 任务分发

	select {} // 保持主进程运行
}
