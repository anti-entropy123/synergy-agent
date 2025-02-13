package main

import (
	"fmt"
	"os"
	"sync"
	"time"

	// "github.com/shirou/gopsutil/cpu"
	// "github.com/shirou/gopsutil/mem"
	"bufio"
	"strconv"
	"strings"
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
func getCPUUsage() float64 {
	// 打开 /proc/stat
	file, err := os.Open("/proc/stat")
	if err != nil {
		fmt.Println("Error reading /proc/stat:", err)
		return 0.0
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	scanner.Scan()
	fields := strings.Fields(scanner.Text())

	// 解析 CPU 时间
	var user, nice, system, idle, iowait, irq, softirq int64
	user, _ = strconv.ParseInt(fields[1], 10, 64)
	nice, _ = strconv.ParseInt(fields[2], 10, 64)
	system, _ = strconv.ParseInt(fields[3], 10, 64)
	idle, _ = strconv.ParseInt(fields[4], 10, 64)
	iowait, _ = strconv.ParseInt(fields[5], 10, 64)
	irq, _ = strconv.ParseInt(fields[6], 10, 64)
	softirq, _ = strconv.ParseInt(fields[7], 10, 64)

	// 计算总时间 & 空闲时间
	totalTime := user + nice + system + idle + iowait + irq + softirq
	idleTime := idle + iowait

	// 等待 50ms 重新读取数据
	time.Sleep(50 * time.Millisecond)

	// 再次读取 CPU 信息
	file.Seek(0, 0)
	scanner = bufio.NewScanner(file)
	scanner.Scan()
	fields = strings.Fields(scanner.Text())

	user2, _ := strconv.ParseInt(fields[1], 10, 64)
	nice2, _ := strconv.ParseInt(fields[2], 10, 64)
	system2, _ := strconv.ParseInt(fields[3], 10, 64)
	idle2, _ := strconv.ParseInt(fields[4], 10, 64)
	iowait2, _ := strconv.ParseInt(fields[5], 10, 64)
	irq2, _ := strconv.ParseInt(fields[6], 10, 64)
	softirq2, _ := strconv.ParseInt(fields[7], 10, 64)

	totalTime2 := user2 + nice2 + system2 + idle2 + iowait2 + irq2 + softirq2
	idleTime2 := idle2 + iowait2

	// 计算 CPU 利用率
	deltaTotal := float64(totalTime2 - totalTime)
	deltaIdle := float64(idleTime2 - idleTime)
	cpuUsage := 100 * (1 - deltaIdle/deltaTotal)

	return cpuUsage
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

// 采集 CPU 和内存数据的 Goroutine
func CollectMetrics() {
	file, err := os.OpenFile("cpu_mem_usage.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Error opening log file:", err)
		return
	}
	defer file.Close()

	node := getNodeName()

	for {
		// 获取 CPU 利用率
		// cpuPercent, _ := cpu.Percent(0, false)
		// 获取内存利用率
		// vmStat, _ := mem.VirtualMemory()

		// 获取 CPU 和内存使用率
		cpuUsage := getCPUUsage()
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

		// 休眠 50ms
		time.Sleep(50 * time.Millisecond)
	}
}
