package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"syscall"
	"time"
	//"runtime"
	//"runtime/debug"
)

var (
	policy   string
	affinity string
)

func main() {
	var rLimit syscall.Rlimit
	err := syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rLimit)
	if err != nil {
		fmt.Println("Error Getting Rlimit ", err)
	}
	//fmt.Println(rLimit)
	rLimit.Max = 1024000
	rLimit.Cur = 1024000
	err = syscall.Setrlimit(syscall.RLIMIT_NOFILE, &rLimit)
	if err != nil {
		fmt.Println("Error Setting Rlimit ", err)
	}
	err = syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rLimit)
	if err != nil {
		fmt.Println("Error Getting Rlimit ", err)
	}
	// fmt.Println("logs Rlimit Final", rLimit)
	flag.StringVar(&policy, "p", "c", "scheduling policys: m:SFS; c:CFS, s: SRTF")
	// var source string
	// flag.StringVar(&source, "t", "", "trace")
	var optimal string
	flag.StringVar(&optimal, "o", "optimal.txt", "STCF optimal values")
	flag.StringVar(&affinity, "a", "0", "set CPU-affinity")
	// cpu := flag.Int("n", 16, "# of cpu cores")
	cpu := 1
	// fmt.Println("logs main cpu", *cpu)
	flag.Parse()
	// fmt.Println("logs main cpu", *cpu)
	//flag.Usage()

	http.HandleFunc("/set_reqs", runFunc(cpu))
	http.HandleFunc("/change_policy", changePolicy)
	go CollectMetrics()                    // 启动监控 Goroutine
	http.HandleFunc("/get_status", status) // 注册 HTTP 端点

	fmt.Println("Starting server on :20251...")
	err = http.ListenAndServe("0.0.0.0:20251", nil)
	if err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func status(w http.ResponseWriter, r *http.Request) {
	Mutex.Lock()
	defer Mutex.Unlock()

	// 返回最近 10 条数据
	n := 10
	if len(StatusDataList) < n {
		n = len(StatusDataList)
	}
	recentData := StatusDataList[len(StatusDataList)-n:]

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(recentData)
}

func changePolicy(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body) // 读取 HTTP 请求体
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}

	content := string(body) // 请求体内容转为字符串

	allowed := []string{"c", "f"} // 允许的策略
	new_policy := ""
	for _, v := range allowed {
		if content == v { // 检查是否是合法的策略
			new_policy = v
			break
		}
	}

	if new_policy == "" { // 如果策略非法，返回错误
		http.Error(w, "wrong policy content", http.StatusInternalServerError)
		return
	}
	fmt.Printf("old policy is %s, will change to %s\n", policy, new_policy)
	policy = new_policy // 更新调度策略
}

func runFunc(cpu int) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}

		trace, num := ParseTrace(strings.Split(string(body), "\n")) // 解析任务请求

		if policy == "c" {
			testCFSWithTraces(cpu, trace, num) // 运行 CFS 调度
		} else if policy == "f" {
			testFIFOWithTraces(cpu, trace, num) // 运行 FIFO 调度
		} else {
			panic("wrong policy") // 非法策略
		}
	}
}

func testSTCF(cpu int, source string, optimal string) {
	// trace, _ := GetTrace(source)
	// Simulate_schedule(trace, optimal, cpu)
}

func testSFS(cpu int, source string) {
	trace, num := GetTrace(source)
	// fmt.Println("num", num)
	testSFSWithTraces(cpu, trace, num)
}

func testSFSWithTraces(cpu int, trace []Action, num int) {
	wg := sync.WaitGroup{}
	cache := make(chan PidI)
	wg.Add(1)
	go Scheduler(&wg, cache, cpu, num)
	for i := 0; i < len(trace); i++ {
		Send(trace[i], cache)
		// job := trace[i]
		// o := time.Now()
		// new_pid := PidI{-10, job.JobName, job.Para1, job.Id, o, -3}
		// cache <- new_pid

		if i < len(trace)-1 {
			time.Sleep(time.Duration(trace[i+1].Start-trace[i].Start) * time.Millisecond)
		}

	}

	wg.Wait()
}

// func parseJSONData(source string) ([]Action, int, error) {
// 	resp, err := http.Get(fmt.Sprintf("http://172.17.0.1:3020/api/acquire_requests/%s", "short"))
// 	if err != nil {
// 		return nil, 0, fmt.Errorf("error fetching trace: %v", err)
// 	}
// 	defer resp.Body.Close()

// 	var data map[string]interface{}
// 	err = json.NewDecoder(resp.Body).Decode(&data)
// 	if err != nil {
// 		return nil, 0, fmt.Errorf("error decoding JSON: %v", err)
// 	}

// 	content := data["content"].([]interface{})
// 	numLong := int(data["num_short"].(float64))

// 	var trace []Action
// 	for _, item := range content {
// 		actionData := item.(map[string]interface{})
// 		trace = append(trace, Action{
// 			JobName: actionData["jobname"].(string),
// 			Exec:    actionData["exec"].(string),
// 			Para1:   int(actionData["para1"].(float64)),
// 			Start:   int(actionData["start"].(float64)),
// 			Id:      int(actionData["id"].(float64)),
// 		})
// 	}

// 	return trace, numLong, nil
// }

// func testSFS(cpu int, source string) {
// 	wg := sync.WaitGroup{}
// 	_, num, _ := parseJSONData(source)
// 	fmt.Println("num", num)
// 	cache := make(chan PidI)
// 	wg.Add(1)
// 	go Scheduler(&wg, cache, cpu, num)
// 	for {
// 		trace, _, err := parseJSONData(source)
// 		if err != nil {
// 			fmt.Println("Error:", err)
// 			continue
// 		}

// 		for i := 0; i < len(trace); i++ {
// 			Send(trace[i], cache)
// 			if i < len(trace)-1 {
// 				time.Sleep(time.Duration(trace[i+1].Start-trace[i].Start) * time.Millisecond)
// 			}
// 		}
// 		wg.Wait()
// 	}
// }

func testFIFO(cpu int, source string) {
	trace, num := GetTrace(source)
	// trace, _, _ := parseJSONData(source)
	testFIFOWithTraces(cpu, trace, num)
}

func testFIFOWithTraces(cpu int, trace []Action, num int) {
	start_time := time.Now() // 记录调度开始时间
	wg := sync.WaitGroup{}

	cache := make(chan PidI)         // 用于存储任务的通道
	// cpuC := GetFifoCpuSingleCpu(cpu) // 获取 FIFO CPU 配置
	wg.Add(len(trace))               // 等待所有任务完成
	for _, v := range trace {
		// wg.Add(1) //每个任务都是依次并发执行的。
		ExecuteNoChannel(&wg, v, "F", cache, start_time, affinity) // 执行任务
	}
	// wg.Wait()

	// 从通道中按顺序读取任务结果
	for i := 0; i < len(trace); i++ {
		<-cache
	}

	wg.Wait()
	close(cache) // 所有协程完成后关闭通道
}

func testCFS(cpu int, source string) {
	trace, num := GetTrace(source)
	// trace, _, _ := parseJSONData(source)
	testCFSWithTraces(cpu, trace, num)
}

func testCFSWithTraces(cpu int, trace []Action, num int) {
	start_time := time.Now()
	wg := sync.WaitGroup{}
	cache := make(chan PidI)
	//go scheduler(&wg,cache)
	// cpuC := GetCFSCpuCores(cpu) // 获取 CFS CPU 配置
	wg.Add(len(trace))
	for i := 0; i < len(trace); i++ {
		ExecuteNoChannel(&wg, trace[i], "N", cache, start_time, affinity)
	}

	//从通道中按顺序读取任务结果
	for i := 0; i < len(trace); i++ {
		<-cache
		if i < len(trace)-1 {
			//timeSleep := time.Duration(trace[i+1].Start-trace[i].Start) * time.Millisecond
			//fmt.Printf("Time difference between tasks %s and %s: %s\n", trace[i].JobName, trace[i+1].JobName, timeSleep)
			time.Sleep(time.Duration(trace[i+1].Start-trace[i].Start) * time.Millisecond)
		}
	}

	wg.Wait()
	close(cache) //所有协程完成后关闭通道
	// lastTaskEndTime := time.Now()
	// fmt.Println("lastTaskEndTime ", lastTaskEndTime)
	// totalElapsedTime := lastTaskEndTime.Sub(firstTaskStartTime)
	// fmt.Println("Total time elapsed:", totalElapsedTime)
}
