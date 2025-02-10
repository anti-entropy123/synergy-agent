package main

import (
	"fmt"
	"strconv"

	//"log"
	"log"
	"os/exec"
	"sync"
	"syscall"
	"time"
	//"sort"
)

var CFS_int int64 = 4
var jobs [1000000]int64    //存储任务的状态(4个状态)
var credits [1000000]int   //存储任务的积分(不一定是任务到达的时间)
var remain [100000]float64 //存储任务的剩余执行时间
var pids [10000000]int     //存储任务的进程ID
var et [1000000]time.Time  //存储任务的时间

func receive(in chan PidI, queue chan PidI, core string, wg *sync.WaitGroup, num int, ts_chan chan PidI, ts *Threshold) {
	//receiver 1)
	//         2) delete jobs if receive the job again
	//         3) send job to first queue
	//fmt.Println("logs receive cpu", core)
	num_job := 0
	var init_credit int
	for {
		select { //监听in管道，起协程，调整积分credit和状态jobs[],将任务传递给下一个队列
		case x := <-in:
			if jobs[x.Id] == 0 && x.Credit == -3 { //任务状态是未执行
				jobs[x.Id] = 1
				if ts.T > 6 {
					init_credit = ts.T //阈值
				} else {
					init_credit = 6
				}
				// new_x := PidI{x.Pid, x.Job, x.N1, x.N2, x.Id, x.St, init_credit}
				new_x := PidI{x.Pid, x.Job, x.N1, x.Id, x.St, init_credit}
				credits[x.Id] = init_credit

				// execute request and also update job direction
				var cmd *exec.Cmd
				// start_time := job.St
				t1 := time.Now()
				fmt.Println("Execute", t1, new_x.Job)
				p := "F"
				if p == "N" {
					cmd = exec.Command("schedtool", "-N", "-a", core, "-e", "python3", "fib.py", strconv.Itoa(new_x.N1), strconv.Itoa(new_x.Id))
					// cmd = exec.Command("schedtool", "-R", "-p", "20", "-a", core, "-e", "python3", "fib.py", strconv.Itoa(new_x.N1), strconv.Itoa(new_x.Id))
				} else {
					//cmd = exec.Command("schedtool","-N","-a",core,"-e","python","fib.py", strconv.Itoa(job.N))
					cmd = exec.Command("schedtool", "-F", "-p", "20", "-a", core, "-e", "python3", "fib.py", strconv.Itoa(new_x.N1), strconv.Itoa(new_x.Id))
				}
				// if p == "N" {
				// 	cmd = exec.Command("schedtool", "-N", "-a", core, "-e", "python3", "benchmark/case6-chameleon/handler.py", strconv.Itoa(job.N1), strconv.Itoa(job.N2), strconv.Itoa(job.Id))
				// } else {
				// 	//cmd = exec.Command("schedtool","-N","-a",core,"-e","python","fib.py", strconv.Itoa(job.N))
				// 	cmd = exec.Command("schedtool", "-F", "-p", "20", "-a", core, "-e", "python3", "benchmark/case6-chameleon/handler.py", strconv.Itoa(job.N1), strconv.Itoa(job.N2), strconv.Itoa(job.Id))
				// }
				err := cmd.Start()
				if err != nil {
					log.Fatal("logs exec 1", err)
				}

				// go Execute(new_x, "F", in, core, queue)
				go Execute(new_x, "F", in, core, queue, cmd, t1)
				ts_chan <- new_x //更新状态、调度策略调整
			} else if jobs[x.Id] == 3 && credits[x.Id] > 0 {
				//sleep & wake jobs
				//fmt.Println("logs this is sleep & waitup jobs")
				jobs[x.Id] = 2
				//任务剩余执行时间与阈值的比例来调整任务的 credit
				cur_credit := int(remain[x.Id] * float64(ts.T))
				// fmt.Println("receive:", "cur_credit ", cur_credit, "remain[x.Id]", remain[x.Id], "ts.T", ts.T, x.Job)
				// new_x := PidI{x.Pid, x.Job, x.N1, x.N2, x.Id, time.Now(), cur_credit}
				new_x := PidI{x.Pid, x.Job, x.N1, x.Id, time.Now(), cur_credit}
				ts_chan <- new_x
				queue <- new_x
			} else {
				jobs[x.Id] = 0
				credits[x.Id] = -2
				num_job += 1
				//fmt.Println("nums", num_job)
				if num_job >= num {
					fmt.Println(num, num_job)
					wg.Done()
					return
				}
			}
			/**
			else{
				//sleep & wake jobs
				fmt.Println("logs this is sleep & waitup jobs")
				jobs[x.Id] = 3
				cur_credit := credits[x.Id]
				new_x := PidI{x.Pid, x.Job, x.N, x.Id,x.St, cur_credit}
				ts_chan <- new_x
				//queue <- new_x
			}
			**/
		}
	}
	//default:
	//continue
}

type Queue struct {
	Core        string
	ExecLength  int //未被调用
	LastLayer   int
	UpdateValue int //状态 1
	FirstLayer  int
}

type Threshold struct {
	T int
}

func calcuMean(n []int) int { //调整阈值
	total := 0
	for _, v := range n {
		total += v
	}
	return total / len(n)
}

// boost sleep jobs

func boostSleepingJobs(in chan PidI) {
	// fmt.Println("普通任务唤醒")
	for {
		for k, v := range jobs { //k、v是jobs数组中的索引和值,k任务id,v任务状态
			if v == 2 { //v == 2是任务休眠状态
				//fmt.Println("logs jobs k, v ", k, v, pids[k])
				if GetProcessState(pids[k]) == 1 { //从休眠被唤醒
					//PidI{0,job.Job,job.N,job.Id,time.Now(), job.Credit}
					//fmt.Println("logs sleeping jobs activate and send")
					// fmt.Println("109 boostSleepingJobs", pids)
					// new_pid := PidI{pids[k], "fib", 20, 20, k, time.Now(), credits[k]}

					var fibString string
					fibString = fmt.Sprintf("fib%d", k)

					new_pid := PidI{pids[k], fibString, 20, k, time.Now(), credits[k]}
					jobs[k] = 3 //任务已经被唤醒
					in <- new_pid
				}
			}
		}
		time.Sleep(time.Duration(1) * time.Millisecond)
	}
}

// // cfs boost policy
// func boostCFSJobs(in chan PidI, threshold int, ts_chan chan PidI) {
// 	fmt.Println("CFS任务唤醒")
// 	for {
// 		for k, v := range jobs {
// 			if v == 4 { //处于CFS的状态
// 				o := time.Now()
// 				//fmt.Println("logs jobs k, v ", k, v)
// 				//检查当前任务距离上次状态变更的时间是否超过指定的阈值
// 				if int(o.Sub(et[k]).Milliseconds()) > threshold && GetProcessState(pids[k]) == 1 {
// 					//PidI{0,job.Job,job.N,job.Id,time.Now(), job.Credit}
// 					//fmt.Println("logs cfs job boost")
// 					// new_pid := PidI{pids[k], "fib", 20, 20, k, time.Now(), credits[k]}

// 					var fibString string
// 					fibString = fmt.Sprintf("fib%d", k)

// 					new_pid := PidI{pids[k], fibString, 20, k, time.Now(), credits[k]}
// 					jobs[k] = 5        //boost cfs policy
// 					in <- new_pid      //入队列
// 					ts_chan <- new_pid //调整阈值
// 				} else if GetProcessState(pids[k]) == 3 { //任务终止
// 					jobs[k] = 6 //更新状态
// 				}
// 			}
// 		}
// 		time.Sleep(time.Duration(1) * time.Millisecond)
// 	}
// }

// threshold policy
func (t *Threshold) AdjustThreshold(ts_chan chan PidI, period int, n int) { //获取任务处理时间间隔更新时间片阈值？
	cur_time := time.Now()
	var interval_time int
	count := 0
	interval_array := make([]int, period)
	for {
		select {
		case _ = <-ts_chan:
			count += 1 //接收到一个任务处理信息
			if count >= period {
				inc_time := time.Now()
				interval_time = int(inc_time.Sub(cur_time).Milliseconds())
				interval_array[count-1] = interval_time //将每个消息的处理时间间隔存放在数组中
				count = 0
				t.T = calcuMean(interval_array) * n //n是绑定的核数，承受多核负载
				interval_array = make([]int, period)
			} else { //记录小于情况下的时间间隔，方便时间间隔平均值的计算
				inc_time := time.Now()
				interval_time = int(inc_time.Sub(cur_time).Milliseconds())
				interval_array[count-1] = interval_time
				cur_time = inc_time //更新cur_time当前时间
			}

		}
	}
}

//var CFS_int int64 = 2

type RWMap struct {
	sync.RWMutex
	m map[string]PidI //传递键值对的数据，例子：m["Pid"] = 123；m["Job"] = "fib1"
}

func (q *Queue) CheckTerminated(job PidI, actions RWMap) int { //Queue类型一个方法,int为返回类型
	va := 0
	if jobs[job.Id] == 0 { //队列检查任务状态，terminated?返回-1?
		va = -1
	} else {
		va = 1
	}
	return va
}

func SwitchFunc(pid int, core string) { //执行CFS算法
	// fmt.Println("cfs")
	fmt.Println("切cfs时间:", time.Now())
	var cmd *exec.Cmd
	cmd = exec.Command("schedtool", "-N", "-a", core, strconv.Itoa(pid))
	// cmd = exec.Command("schedtool", "-R", "-p", "20", "-a", core, strconv.Itoa(pid))
	err := cmd.Start()
	if err != nil {
		log.Fatal(err)
	}
	cmd.Wait()
}

func UpdateFunc(pid int, core string, p string) { //执行FIFO算法
	// fmt.Println("fifo")
	fmt.Println("切fifo时间:", time.Now(), "p值:", p)
	var cmd *exec.Cmd
	cmd = exec.Command("schedtool", "-F", "-p", p, "-a", core, strconv.Itoa(pid))
	err := cmd.Start()
	if err != nil {
		log.Fatal(err)
	}
	cmd.Wait()
}

func UpdateCFScore(direct int, cfs_value int64, update_v int) int64 { //更新CFS分数，目前没有被调用
	if direct == -1 {
		return cfs_value - int64(update_v)
	} else {
		return cfs_value + int64(update_v)
	}
}

func (q *Queue) Schedule(actions RWMap, cache chan PidI, in chan PidI, out chan PidI, cfs_chan chan PidI, cpu int, ts *Threshold) {
	//每个CPU核心的协程执行相应Queue的Schedule方法
	on := 1
	count := 0
	s1 := 0
	for {
		select {
		//receive jobs from prev layer
		case x, _ := <-in:
			pids[x.Id] = x.Pid
			if q.FirstLayer == 1 {
				fmt.Println("logs q1 Time start", time.Now(), x.Job)
			}
			s1 = 0
			//fmt.Println("logs path", q.Core, x)
			//logs path 0x1 {227 fib4 34 4 2023-08-25 12:55:31.494226235 +0000 UTC m=+0.001010932 20}
			if on == 0 { //on为0表示队列处于关闭状态
				//new_pid := PidI{-1, "minus", q.UpdateValue, q.UpdateValue, -1, time.Now(), x.Credit} //q.UpdateValue值为1
				//new_pid := PidI{-1, "minus", 100, 100, -1, time.Now(), x.Credit} // x.Credit的值为20
				// fmt.Println("on == 0 x.Credit", x.Credit)
				new_pid := PidI{-1, "minus", q.UpdateValue, -1, time.Now(), x.Credit}
				cfs_chan <- new_pid
				on = 1
			}

			// o := time.Now() //超过3倍设定时间片的值，就会休眠？注释掉短任务20-26，执行固定大小时间片FIFO基本按顺序打印出结果
			// // use default cfs scheduleor
			// if int(o.Sub(x.St).Milliseconds()) > 3*ts.T { //ts.T的值为20
			// 	// fmt.Println("3*ts.T x.Credit", x.Credit, x.Job)
			// 	fmt.Println("超过3*ts.T休眠", x.Credit, x.Job)
			// 	jobs[x.Id] = 2 //休眠状态
			// 	credits[x.Id] = x.Credit
			// 	cfs_chan <- x
			// 	pids[x.Id] = x.Pid
			// 	et[x.Id] = time.Now()
			// 	continue
			// }

			//actions.Lock()
			// fmt.Println("UpdataFunc 30 start", x.Job)
			UpdateFunc(x.Pid, q.Core, "30") //执行FIFO算法
			// fmt.Println("UpdataFunc 30 end", x.Job)
			//x.Credit\ts.T\credits[x.Id]:20
			// fmt.Println("fifo 30")
			//actions.Unlock()
			exec_time := 0
			// fmt.Println("Schedule ts.T", ts.T, x.Job)
			if ts.T == 0 {
				exec_time = 6
			} else {
				exec_time = ts.T
			}
			if credits[x.Id] > 0 {
				exec_time = credits[x.Id]
			}

			// for s1 < exec_time {
			// 	time.Sleep(time.Duration(1) * time.Millisecond)
			// 	s1 += 1
			// 	if q.CheckTerminated(x, actions) == -1 {
			// 		break
			// 	} else if GetProcessState(x.Pid) == 2 {
			// 		jobs[x.Id] = 2
			// 		credits[x.Id] = x.Credit - s1
			// 		remain[x.Id] = float64(x.Credit - s1)
			// 		break
			// 	}
			// 	if s1 >= x.Credit {
			// 		break
			// 	}
			// }

			//s1很重要，决定执行fifo的时间片大小和核实切换到CFS
			//exec_time:20;s1:
			//打印一个时间戳a
			a := time.Now()
			for true { //s1作业时机执行时间累加
				// fmt.Println("fifo 30 s1 < exec_time", exec_time, x.Job)
				time.Sleep(time.Duration(1) * time.Millisecond)
				s1 += 1 //s1一直累加到输入的ts.T退出循环
				//打印一个时间戳b,用b-a,看看b-a的值是否大于s1，大于s1则break
				b := time.Now()
				if (int(b.Sub(a).Milliseconds())) > exec_time {
					fmt.Println("b-a ", int(b.Sub(a).Milliseconds()), x.Job)
					break
				}
				if q.CheckTerminated(x, actions) == -1 { //作业终止为-1
					break
				} else if GetProcessState(x.Pid) == 2 { //作业休眠
					jobs[x.Id] = 2
					//x.Credit 是作业初始的积分值
					//credits[x.Id] 是作业在执行过程中实时跟踪的当前积分值
					//remain[x.Id] 用于追踪作业的剩余执行时间
					fmt.Println("作业休眠:", "x.Credit ", x.Credit, "s1 ", s1, "credits[x.Id] ", credits[x.Id], "remain[x.Id] ", remain[x.Id], x.Job)
					credits[x.Id] = x.Credit - s1
					remain[x.Id] = float64(x.Credit - s1)
					break
				}
				if s1 >= x.Credit { //大于作业执行时间
					break
				}
			}

			if q.LastLayer != 1 {
				// fmt.Println("fifo 20")
				//x.Pid是执行的fib.py的进程id
				go UpdateFunc(x.Pid, q.Core, "20") //起协程执行FIFO算法
				//SwitchFunc(x.Pid, GetCFSCpuCores(cpu))
				out <- x
			} else {
				//UpdateFunc(x.Pid, q.Core, "20")
				fmt.Println("切cfs", x.Job)
				go SwitchFunc(x.Pid, GetCFSCpuCores(cpu))
				cfs_chan <- x
				if jobs[x.Id] != 2 {
					//4 means cfs state
					jobs[x.Id] = 4
				}
				pids[x.Id] = x.Pid
				et[x.Id] = time.Now()
			}
			//}
		default: //没有任务时，进行短暂休眠
			time.Sleep(time.Duration(1) * time.Millisecond)
			count += 1
			if count >= 2 && on == 1 {
				//new_pid := PidI{-1, "plus", q.UpdateValue, q.UpdateValue, -1, time.Now(), 20} //q.UpdateValue的默认值为1
				// new_pid := PidI{-1, "plus", 100, 100, -1, time.Now(), 20} //20为Credit int
				new_pid := PidI{-1, "minus", q.UpdateValue, -1, time.Now(), 20}
				cfs_chan <- new_pid
				on = 0
				count = 0
			} else if on != 1 {
				count = 0
			}
		}
	}
}

func HandleCFSChan(actions RWMap, in chan PidI, m map[string]int, cfs_value int64) {
	//do nothing
	var a int64 = 0
	for {
		select {
		case x, _ := <-in:
			a += 1 //仅对接收消息进行了计数
			if a >= 10000 && x.Pid == -1 {
				fmt.Println(a)
			}
		}
	}
}

func Scheduler(wg *sync.WaitGroup, cache chan PidI, cpu int, num int) { //一个核，一个队列，一个Schedule方法
	defer wg.Done()                //（无论是正常结束还是出现 panic），WaitGroup 中的计数器减一
	wg_receive := sync.WaitGroup{} //等待协程完成
	var rLimit syscall.Rlimit
	err := syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rLimit)
	if err != nil {
		fmt.Println("Error Getting Rlimit ", err)
	}
	tsChan := make(chan PidI)
	chan1 := make(chan PidI)
	chan2 := make(chan PidI)
	//chan3 := make(chan PidI)
	cfs_chan := make(chan PidI)
	con_map := make(map[string]int)
	actions := make(map[string]PidI)
	con_actions := RWMap{m: actions} //带读写锁的映射，存储和传递一些任务相关状态信息
	// ts_instance决定fifo执行时间片的大小
	ts_instance := Threshold{20} //20仅初始化Threshold结构体实例，后续根据任务处理情况动态调整
	//layer 1
	var queues [1024]Queue //数组中每个元素都是一个Queue类型结构体，创建1024个队列，每个队列都有不同核心、执行长度、最后一层标志、状态更新值、第一层标志
	for i := 0; i < cpu; i++ {
		// fmt.Println("logs cpu", i)
		queues[i] = Queue{GetFifoCpuSingleCpu(i), 20, 1, 1, 1} //这里是赋值给type Queue struct,20是最大队列值
	}
	for i := 0; i < cpu; i++ {
		// fmt.Println("logs cpu", i)
		//每个协程运行一个CPU核心对应的调度队列，独立协程执行Schedule方法
		go queues[i].Schedule(con_actions, cache, chan1, chan2, cfs_chan, cpu, &ts_instance)
	}
	go HandleCFSChan(con_actions, cfs_chan, con_map, int64(2))
	wg_receive.Add(1)
	go receive(cache, chan1, GetCFSCpuCores(cpu), &wg_receive, num, tsChan, &ts_instance)
	go ts_instance.AdjustThreshold(tsChan, 200, cpu) //将中间传入的参数period设置很大就不会在高负载时发生时间片的动态更改
	go boostSleepingJobs(chan1)
	//go boostCFSJobs(chan1, 20000, tsChan)
	wg_receive.Wait()

}
