package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"syscall"

	// "os"
	"os/exec"
	"strconv"
	"sync"
	"time"
)

type PidI struct { //fib1 fib.py 27 5 1
	Pid int    //进程id
	Job string //fib1
	N1  int
	// N2     int
	Id     int //最后一列的id号
	St     time.Time
	Credit int
}

func Send(job Action, pids chan PidI) {
	// Send just send request to receiver
	o := time.Now()
	//time.Sleep(time.Duration(job.Start)*time.Millisecond)
	new_pid := PidI{-10, job.JobName, job.Para1, job.Id, o, -3}
	// new_pid := PidI{-10, job.JobName, job.Para1, job.Para2, job.Id, o, -3}
	pids <- new_pid
}

func Execute(job PidI, p string, pids chan PidI, core string, queue chan PidI, cmd *exec.Cmd, t1 time.Time) {
	// // execute request and also update job direction
	// var cmd *exec.Cmd
	// // start_time := job.St
	// t1 := time.Now()
	// fmt.Println("Execute", t1, job.Job)
	// if p == "N" {
	// 	cmd = exec.Command("schedtool", "-N", "-a", core, "-e", "python3", "fib.py", strconv.Itoa(job.N1), strconv.Itoa(job.Id))
	// } else {
	// 	//cmd = exec.Command("schedtool","-N","-a",core,"-e","python","fib.py", strconv.Itoa(job.N))
	// 	cmd = exec.Command("schedtool", "-F", "-p", "20", "-a", core, "-e", "python3", "fib.py", strconv.Itoa(job.N1), strconv.Itoa(job.Id))
	// }
	// // if p == "N" {
	// // 	cmd = exec.Command("schedtool", "-N", "-a", core, "-e", "python3", "benchmark/case6-chameleon/handler.py", strconv.Itoa(job.N1), strconv.Itoa(job.N2), strconv.Itoa(job.Id))
	// // } else {
	// // 	//cmd = exec.Command("schedtool","-N","-a",core,"-e","python","fib.py", strconv.Itoa(job.N))
	// // 	cmd = exec.Command("schedtool", "-F", "-p", "20", "-a", core, "-e", "python3", "benchmark/case6-chameleon/handler.py", strconv.Itoa(job.N1), strconv.Itoa(job.N2), strconv.Itoa(job.Id))
	// // }
	// err := cmd.Start()
	// if err != nil {
	// 	log.Fatal("logs exec 1", err)
	// }
	// tw := time.Now()
	// fmt.Println("logs wait time",tw.Sub(t1))
	//actions.m[job.Job] = cmd.Process.Pid
	//new_pid := PidI{0,job.Job,job.N,job.Id}
	pid := cmd.Process.Pid
	var new_pid PidI
	// if cmd != nil {
	// 	new_pid = PidI{pid, job.Job, job.N1, job.N2, job.Id, time.Now(), job.Credit}
	// } else {
	// 	new_pid = PidI{0, job.Job, job.N1, job.N2, job.Id, time.Now(), job.Credit}
	// }
	if cmd != nil {
		new_pid = PidI{pid, job.Job, job.N1, job.Id, time.Now(), job.Credit}
	} else {
		new_pid = PidI{0, job.Job, job.N1, job.Id, time.Now(), job.Credit}
	}
	queue <- new_pid
	// fmt.Println("pid", pid, job.Job)
	err := cmd.Wait()
	if err != nil {
		log.Fatal("exec 2", err)
	}
	t2 := time.Now()
	fmt.Println("cmd.Wait", t2, ", context switch ", cmd.ProcessState.SysUsage().(*syscall.Rusage).Nivcsw, job.Job)
	fmt.Println("User CPU Time ", cmd.ProcessState.SysUsage().(*syscall.Rusage).Utime, job.Job)
	// fmt.Println("System CPU Time ", cmd.ProcessState.SysUsage().(*syscall.Rusage).Stime, job.Job)
	new_pid.Credit = -2
	pids <- new_pid
	fmt.Println(job.Job, t2.Sub(t1).Milliseconds())
	// fmt.Println("logs TIME: ", job.Job, t1.Sub(start_time), t2.Sub(start_time))
}

func ExecuteNoChannel(wg *sync.WaitGroup, job Action, p string, pids chan PidI, start_time time.Time, cpuC string) {
	defer wg.Done()
	//time.Sleep(time.Duration(job.Start) * time.Millisecond)
	t1 := time.Now()
	fmt.Println("ExecuteNoChannel", t1, job.JobName)
	var cmd *exec.Cmd
	// if p == "N" {
	// 	cmd = exec.Command("schedtool", "-N", "-a", cpuC, "-e", "python3", job.Exec, strconv.Itoa(job.Para1), strconv.Itoa(job.Para2), strconv.Itoa(job.Id))
	// } else {
	// 	cmd = exec.Command("schedtool", "-R", "-p", "20", "-a", "0x1", "-e", "python3", job.Exec, strconv.Itoa(job.Para1), strconv.Itoa(job.Para2), strconv.Itoa(job.Id))
	// }
	if p == "N" {
		cmd = exec.Command("schedtool", "-N", "-a", cpuC, "-e", "python3", job.Exec, strconv.Itoa(job.Para1), strconv.Itoa(job.Id))
	} else {
		cmd = exec.Command("schedtool", "-F", "-p", "20", "-a", cpuC, "-e", "python3", job.Exec, strconv.Itoa(job.Para1), strconv.Itoa(job.Id))
	}

	//创建一个管道来捕获标准输出
	stdout, err := cmd.StderrPipe()
	if err != nil {
		log.Fatal("Failed to create StdoutPipe:", err)
	}

	err = cmd.Start()
	if err != nil {
		log.Fatal("exec 1", err)
	}
	// tw := time.Now()
	// fmt.Println("logs wait time", tw.Sub(t1))
	//pid := cmd.Process.Pid
	//new_pid := PidI{cmd.Process.Pid,job.JobName}
	//pids <- new_pid
	//err := cmd.Wait()
	//if err != nil{
	//        log.Fatal(err)
	//}
	go func() { // 任务的执行顺序是并发的，每个任务的执行不受前一个任务的影响。
		//读取标准输出的内容
		// output, err := ioutil.ReadAll(stdout)
		_, err := ioutil.ReadAll(stdout)
		if err != nil {
			log.Fatal("Failed to read stdout:", err)
		}

		//输出命令的标准输出
		//fmt.Println(job.JobName, "Command output:\n", string(output))

		err = cmd.Wait() // 等待命令执行完成
		if err != nil {
			log.Fatal("exec 2", err)
		}

		t2 := time.Now()
		fmt.Println("cmd.Wait", t2, ", context switch ", cmd.ProcessState.SysUsage().(*syscall.Rusage).Nivcsw, job.JobName)
		fmt.Println("User CPU Time ", cmd.ProcessState.SysUsage().(*syscall.Rusage).Utime, job.JobName)

		fmt.Println(job.JobName, t2.Sub(t1).Milliseconds())
		//fmt.Println(t2.Sub(t1).Milliseconds())
		//fmt.Println("logs TIME: ", job.JobName, t1.Sub(start_time), t2.Sub(start_time))

		// 通知主线程当前任务已经完成
		// new_pid := PidI{cmd.Process.Pid, job.JobName, job.Para1, job.Para2, job.Id, t2, -3}
		// fmt.Println("new_pid ", new_pid)
		new_pid := PidI{cmd.Process.Pid, job.JobName, job.Para1, job.Id, t2, -3}
		pids <- new_pid
	}()
}
