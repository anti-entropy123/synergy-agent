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
            #    0            1            2            3 4  5  6
            # fib5 10:25:21.596 10:25:21.601 10:25:21.665 5 63 69
            fields = line.split()
            name = fields[0]
            if len(fields) == 7 and name in items:
                items[name]["t0"] = fields[1]
                items[name]["t1"] = fields[2]
                items[name]["t2"] = fields[3]
                items[name]["t1-t0"] = fields[4]
                items[name]["t2-t1"] = fields[5]
                items[name]["turn-round time"] = fields[6]
            # else:
            #     print(f"{name} cpu time not found")

# 写入 CSV 文件
with open(output_name, "w") as f:
    f.write("proc_name,t0,t1,t2,t1-t0,t2-t1,cpu time,turn-round time\r\n")
    for k, v in items.items():
        # f.write(f'{k},{v["cpu time"]},{v.get("turn-round time", "N/A")}\r\n')
        # 将 t0 t1 t2 t1-t0, t2-t1, t2-t0 等字段写入一行
        f.write(f'{k},{v["t0"]},{v["t1"]},{v["t2"]},{v["t1-t0"]},{v["t2-t1"]},{v["cpu time"]},{v["turn-round time"]}\r\n')

print(f"Log data processed successfully. Output saved to {output_name}")
