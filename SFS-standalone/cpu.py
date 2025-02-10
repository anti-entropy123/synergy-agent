import psutil
import subprocess
import time

def get_process_cpu_usage(process):
    """
    Get the CPU usage of a specific process.

    :param process: psutil.Process object
    :return: List of CPU usage percentages for each core
    """
    try:
        # This gives the CPU usage for the process over all cores
        process_cpu_percent = process.cpu_percent(interval=0.0005) / psutil.cpu_count()
        # This gives the overall CPU usage per core
        overall_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
        return process_cpu_percent, overall_cpu_percent
    except psutil.NoSuchProcess:
        return None, None

def collect_cpu_usage(command, interval=0.0005, duration=600, cpu_core=0, output_file="cpu_usage.txt"):
    """
    Collect CPU usage of a specific command every interval seconds for a duration of time and save to a file.

    :param command: Command to be executed
    :param interval: Time in seconds between each collection
    :param duration: Total duration of collection in seconds
    :param cpu_core: The CPU core to bind the process to
    :param output_file: File to save the CPU usage data
    """
    # Start the command using taskset to bind to a specific CPU core
    taskset_command = f"taskset -c {cpu_core} {command}"
    process = subprocess.Popen(taskset_command, shell=True)
    ps_process = psutil.Process(process.pid)

    with open(output_file, 'w') as f:
        end_time = time.time() + duration
        while time.time() < end_time:
            process_cpu_usage, overall_cpu_usage = get_process_cpu_usage(ps_process)
            if process_cpu_usage is not None:
                data_line = f"CPU Usage for '{command}' on CPU core {cpu_core}: {process_cpu_usage:.2f}%\n"
                overall_usage_line = f"Overall CPU Usage per core: {overall_cpu_usage}\n"
                f.write(data_line)
                f.write(overall_usage_line)
                f.flush()  # Ensure data is written to file immediately
                print(data_line.strip())
                print(overall_usage_line.strip())
            else:
                f.write(f"Process '{command}' has ended.\n")
                f.flush()
                print(f"Process '{command}' has ended.")
                break
            time.sleep(interval)

    process.terminate()
    process.wait()

if __name__ == "__main__":
    command = "schedtool -F -p 20"  # Replace with your command
    collect_cpu_usage(command, interval=0.0005, duration=600, cpu_core=0)
