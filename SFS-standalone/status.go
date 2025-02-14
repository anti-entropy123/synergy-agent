package main

import (
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/shirou/gopsutil/v3/cpu"
	// "github.com/shirou/gopsutil/cpu"
	// "github.com/shirou/gopsutil/mem"
)

type StatusData struct {
	Timestamp int64   `json:"timestamp"`
	CPUUsage  float64 `json:"cpu_usage"`
	// MemUsage  float64 `json:"mem_usage"`
	Policy string `json:"policy"`
	Node   string `json:"node"`
}

var (
	StatusDataList []StatusData
	Mutex          sync.Mutex
)

// 读取 `/proc/stat` 获取 CPU 时间信息
func getCPUUsage(cpuid int) (float64, error) {
	percentages, err := cpu.Percent(time.Second, true) // true 表示返回每个核心的负载
	if err != nil {
		return 0, err
	}

	if cpuid >= len(percentages) {
		return 0, fmt.Errorf("CPU %d 不存在", cpuid)
	}

	return percentages[cpuid], nil

}

// // 读取 `/proc/meminfo` 获取内存使用率
// func getMemUsage() float64 {
// 	// 打开 /proc/meminfo
// 	file, err := os.Open("/proc/meminfo")
// 	if err != nil {
// 		fmt.Println("Error reading /proc/meminfo:", err)
// 		return 0.0
// 	}
// 	defer file.Close()

// 	var memTotal, memAvailable int64
// 	scanner := bufio.NewScanner(file)

// 	for scanner.Scan() {
// 		fields := strings.Fields(scanner.Text())
// 		if len(fields) < 2 {
// 			continue
// 		}

// 		if fields[0] == "MemTotal:" {
// 			memTotal, _ = strconv.ParseInt(fields[1], 10, 64)
// 		} else if fields[0] == "MemAvailable:" {
// 			memAvailable, _ = strconv.ParseInt(fields[1], 10, 64)
// 		}

// 		// 读取到 MemAvailable 即可退出
// 		if memTotal > 0 && memAvailable > 0 {
// 			break
// 		}
// 	}

// 	// 计算内存使用率
// 	memUsage := 100 * (1 - float64(memAvailable)/float64(memTotal))
// 	return memUsage
// }

func getNodeName() string {
	hostname, err := os.Hostname()
	if err != nil {
		return "unknown"
	}
	return hostname
}

// 采集 CPU 和内存数据
func CollectMetrics(affinity int) {
	file, err := os.OpenFile("cpu_mem_usage.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Error opening log file:", err)
		return
	}
	defer file.Close()

	node := getNodeName()

	// 获取 CPU 利用率
	// cpuPercent, _ := cpu.Percent(0, false)
	// 获取内存利用率
	// vmStat, _ := mem.VirtualMemory()

	// 获取 CPU 和内存使用率
	cpuUsage, err := getCPUUsage(affinity)
	if err != nil {
		fmt.Printf("get CPU Usage failed, err=%s\n", err)
	}
	// memUsage := getMemUsage()

	// 记录时间戳
	timestamp := time.Now().UnixMilli()

	// 存入全局变量
	Mutex.Lock()
	data := StatusData{
		Timestamp: timestamp,
		// CPUUsage:  cpuPercent[0],      // CPU 利用率（单核平均）
		// MemUsage:  vmStat.UsedPercent, // 内存使用率
		CPUUsage: cpuUsage,
		// MemUsage: memUsage,
		Policy: policy,
		Node:   node,
	}
	StatusDataList = append(StatusDataList, data)
	if len(StatusDataList) > 1000 { // 只保留最近 1000 条数据
		StatusDataList = StatusDataList[len(StatusDataList)-1000:]
	}
	Mutex.Unlock()

	// 追加写入日志文件
	// logEntry := fmt.Sprintf("%d,%.2f,%.2f,%s,%s\n", timestamp, data.CPUUsage, data.MemUsage, data.Policy, data.Node)
	logEntry := fmt.Sprintf("%d,%.2f,%s,%s\n", timestamp, data.CPUUsage, data.Policy, data.Node)
	file.WriteString(logEntry)

}
