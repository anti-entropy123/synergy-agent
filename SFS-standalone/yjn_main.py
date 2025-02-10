import psutil
import time

target_process_name = "main"
sleep_interval = 0.05 # 50 ms

def wait_to_find_process_by_name() -> int:
    while True:
        for process in psutil.process_iter(['name', 'pid', 'status']):
            if process.info['name'] == target_process_name:
                print(f"进程名: {process.info['name']}, 进程ID: {process.info['pid']}, 状态: {process.info['status']}")
                return process.info['pid']
        
        print("未识别到你的进程...")
        time.sleep(0.5)

def pid_exists(pid):
    return psutil.pid_exists(pid)

def get_cpu_load(core):
    cpu_percent = psutil.cpu_percent(percpu=True)
    return cpu_percent[core]

if __name__ == "__main__":
    core = 1
    pid = wait_to_find_process_by_name()
    cpu_loads = []

    while True:
        cpu_load = get_cpu_load(core)
        print(f"当前核心{core}的负载是 {cpu_load}%")
        cpu_loads.append(cpu_load)
        if not pid_exists(pid):
            break
        else:
            time.sleep(sleep_interval)
    
    print(f"average cpu load: {sum(cpu_loads)/len(cpu_loads)}%")
