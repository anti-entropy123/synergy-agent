package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

const MAX_RUNNINGTIME = 2147483647

type Exec struct {
	Ac  Action
	Opt int
}

func Read_optimal(path string) map[int]int {
	//return map[int]int
	file, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}

	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var txtlines []string
	for scanner.Scan() {
		txtlines = append(txtlines, scanner.Text())
	}
	dic := make(map[int]int)
	var s []string
	var n int //对应输入参数
	var t int //对应参数所需要花费的执行时间
	for _, eachline := range txtlines {
		s = strings.Split(eachline, " ")
		n, _ = strconv.Atoi(s[0])
		t, _ = strconv.Atoi(s[1])
		dic[n] = t
	}
	return dic
}

func check_in_select(selected []int, id int) bool { //检查任务是否被选中，id在action中，[]int存放id
	for _, v := range selected {
		if v == id {
			return true
		}
	}
	return false
}

func Simulated_execute(workloads []Exec, c_time int, n int) []Exec { //workloads多个 Exec 结构的切片
	//c_time表示模拟执行任务调度的当前时间
	//var limit int
	//if c_time >= len(workloads){
	//	limit = len(workloads)
	//}else{
	//	limit = c_time
	//}
	temp := 0
	for k, v := range workloads {
		if v.Ac.Start > c_time {
			//fmt.Println("logs", "start time", c_time,v.Ac)
			temp = k - 1
			break
		}
		//如果所有任务的启动时间都小于等于当前时间 c_time，则 temp 最终会被更新为 len(workloads)，表示所有任务都已经启动
		temp = len(workloads)
	}
	//if temp == -1{
	//	temp = len(workloads)
	//}
	if temp < 0 {
		temp = 0
	}
	running_jobs := workloads[:temp]
	//fmt.Println(c_time, workloads[:temp])
	var selected_id []int
	//从正在运行的任务列表中选择 n 个任务执行
	for i := 0; i < n; i++ {
		max_v := MAX_RUNNINGTIME
		id := -1
		//在正在运行的任务列表中找到具有最小优先级的任务
		for k, v := range running_jobs {
			if v.Opt < max_v && !check_in_select(selected_id, k) {
				max_v = v.Opt
				id = k
			}
		}
		// 如果找到了任务，将其ID添加到已选中的任务列表中
		if max_v != MAX_RUNNINGTIME && id != -1 {
			//fmt.Println(id, max_v)
			selected_id = append(selected_id, id)
		}
	}
	//fmt.Println(c_time, selected_id)
	//fmt.Println(running_jobs)
	// 根据已选中的任务列表更新正在运行的任务列表
	for _, v := range selected_id {
		//fmt.Println(c_time, workloads[v])
		running_jobs[v].Opt -= 1
		// 如果任务的优先级达到了0，将其重置为最大优先级，并输出执行信息 [任务执行结束]
		if running_jobs[v].Opt <= 0 {
			running_jobs[v].Opt = MAX_RUNNINGTIME
			s := strconv.Itoa(c_time - workloads[v].Ac.Start) //任务已经执行的时间
			//这里没有体现SRTF，任务完成所需剩余时间
			//remainingTime := workloads[v].Ac.TotalExecTime - (c_time - workloads[v].Ac.Start)
			fmt.Println(workloads[v].Ac.JobName, s)
		}
	}
	return workloads
}

func check_finished(workloads []Exec) bool {
	for _, v := range workloads {
		if v.Opt != MAX_RUNNINGTIME {
			return false
		}
	}
	return true
}

func Simulate_schedule(trace []Action, opt_f string, n int) { //action、文件路径、cpu核心
	var workloads []Exec       //存储任务和优先级
	dic := Read_optimal(opt_f) //读取文件，得到优先级映射表
	for _, v := range trace {  //v 是 Action 结构的一个实例
		// //对应fib.py的一个参数
		// workloads = append(workloads,Exec{v, dic[v.Para]})
		//对应chameleon.py的两个参数，由于两个参数都有一样的，这里选取第一个参数
		workloads = append(workloads, Exec{v, dic[v.Para1]})
	}
	c_time := 0
	for {
		workloads = Simulated_execute(workloads, c_time, n)
		c_time += 1
		if check_finished(workloads) {
			return
		}
	}
}
