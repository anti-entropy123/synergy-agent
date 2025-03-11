import random
import pandas as pd
import numpy as np

# 定义占比数据-华为
# ratios = {
#     20: 51.89,
#     21: 0.84,
#     22: 0.14,
#     23: 1.89,
#     24: 4.83,
#     25: 0.63,
#     26: 3.15,
#     27: 0.14,
#     28: 2.87,
#     29: 8.54,
#     30: 7.56,
#     31: 3.50,
#     32: 4.27,
#     33: 5.04,
#     34: 2.17,
#     35: 2.52
# }

ratios = {
    20: 51.89,
    21: 0.84 + 2.52 + 2.17 + 5.04,
    22: 0.14,
    23: 1.89,
    24: 4.83,
    25: 0.63,
    26: 3.15,
    27: 0.14,
    28: 2.87,
    29: 8.54,
    30: 7.56,
    31: 6.50,
    32: 1.27,
}

# # 定义占比数据-华为
# ratios = {
#     20: 69.8,
#     27: 23.2,
#     30: 6,
#     32: 1
# }

# # 定义占比数据-微软
# ratios = {
#     20: 12.29,
#     21: 0.71,
#     22: 0.59,
#     23: 4.43,
#     24: 2.34,
#     25: 2.67,
#     26: 4.83,
#     27: 4.55,
#     28: 5.36,
#     29: 5.69,
#     30: 6.59,
#     31: 5.80,
#     32: 6.67,
#     33: 5.57,
#     34: 6.31,
#     35: 25.60
# }

# # 定义占比数据-微软
# ratios = {
#     20: 42.9,
#     27: 17.2,
#     30: 16.7,
#     32: 23.2
# }

# 计算每个数值对应的数量
low_load_interval = 50
low_load_interval_time = 2000
total_samples = 500

counts = {k: int(v / 100 * total_samples) for k, v in ratios.items()}

# 确保总数为 1000，调整误差
actual_total = sum(counts.values())
diff = total_samples - actual_total
keys = list(counts.keys())

# 调整误差
for _ in range(abs(diff)):
    if diff > 0:
        counts[random.choice(keys)] += 1
    elif diff < 0:
        key = random.choice([k for k in keys if counts[k] > 0])
        counts[key] -= 1

# 生成测试数据
data = []
index = 1

# 按照顺序生成
# for value, count in counts.items():
#     for _ in range(count):
#         data.append([f"fib{index}", "fib.py", value, 0, index])  # 第三列按照比例分配，最后一列从1递增
#         index += 1

# 将所有的 Line（第三列）值按照占比要求生成
lines = []
for value, count in counts.items():
    for _ in range(count):
        lines.append(value)

# 打乱第三列数据
random.shuffle(lines)


# 根据打乱后的数据生成对应的数据行
for i in range(total_samples):
    # 使用泊松分布生成第四列数据，lambda 参数可以根据需求调整
    if (i + 1) % low_load_interval == 0:
        arrival_time = low_load_interval_time
    else:
        arrival_time = np.random.poisson(0.1)  # 这里假设 λ = 1，表示事件平均每单位时间发生1次
    
    data.append([f"fib{i+1}", "fib.py", lines[i], arrival_time, i+1])  # 第三列打乱，最后一列从1递增

# 转换为 DataFrame
df = pd.DataFrame(data, columns=["ID", "Script", "Line", "Arg1", "Arg2"])

# 保存为 CSV 文件
# csv_filename = "hw_1000.csv"
# csv_filename = "hw.csv"
csv_filename = f"hw_{total_samples}_luan_poisson"
df.to_csv(csv_filename, index=False, header=False, sep=' ')

print(f"CSV 文件已生成: {csv_filename}")
