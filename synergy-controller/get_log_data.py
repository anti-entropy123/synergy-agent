import re
import sys

# 确保提供了正确的命令行参数
if len(sys.argv) != 3:
    print("Usage: python3 get_log_data.py <input_log_file> <output_csv_file>")
    sys.exit(1)

source_name = sys.argv[1]  # 输入日志文件名
output_name = sys.argv[2]  # 输出 CSV 文件名

items = {}

# 读取日志文件并解析数据
with open(source_name) as f:
    for line in f.readlines():
        if line.startswith("User CPU Time  {"):
            matches = re.search(r'\{(\d+\s+\d+)\}', line)
            if matches:
                sec, usec = map(int, matches.group(1).split())
                matches = re.search(r'fib\d+', line)
                if matches:
                    proc_name = matches.group()
                    items[proc_name] = {"cpu time": sec * 1000 + usec // 1000}
        elif line.startswith("fib"):
            fields = line.split()
            if len(fields) == 2 and fields[0] in items:
                items[fields[0]]["turn-round time"] = fields[1]

# 写入 CSV 文件
with open(output_name, "w") as f:
    f.write("proc_name,cpu time,turn-round time\r\n")
    for k, v in items.items():
        f.write(f'{k},{v["cpu time"]},{v.get("turn-round time", "N/A")}\r\n')

print(f"Log data processed successfully. Output saved to {output_name}")
