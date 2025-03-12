import matplotlib

# 分别读取 result_Synergy_CDF_hw_500_luan_poisson/result/agent1_4.csv 和 result_OpenFaaS_CDF_hw_500_luan_poisson/result/agent11_14.csv
# 将两个文件的第三列分别放在两个数组里：
import pandas as pd

trace = "wr"

# 读取第一个CSV文件
df1 = pd.read_csv(f'/home/tank/chm/synergy-agent/synergy-controller/export/result_Synergy_CDF_{trace}_500_luan_poisson/result/agent1_8.csv')

# 读取第二个CSV文件
df2 = pd.read_csv(f'/home/tank/chm/synergy-agent/synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')

df3 = pd.read_csv(f'/home/tank/chm/synergy-agent/synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')

df4 = pd.read_csv(f'/home/tank/chm/synergy-agent/synergy-controller/export/result_SFS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')

print(f"{len(df1)}, {len(df2)}, {len(df3)}, {len(df4)}")
assert(len(df1) == len(df2) and len(df1) == len(df3) and len(df1) == len(df4),)

# ratio = 0.9
for ratio in range(50, 101, 10):
    ratio /= 100
    print("\nratio: ", ratio)
    print("synergy:", df1["turn-round time"][:int(ratio*len(df1))].mean())
    # with open("/home/tank/chm/synergy-agent/synergy-controller/export/result_Synergy_CDF_{trace}500_luan_poisson/result/agent1_4.csv.txt", "r") as f:
    #     print(f.readlines()[-1])
    print("openfaas", df2["turn-round time"][:int(ratio*len(df1))].mean())
    # with open("/home/tank/chm/synergy-agent/synergy-controller/export/result_OpenFaaS_CDF_{trace}500_luan_poisson/result/agent11_14.csv.txt", "r") as f:
    #     print(f.readlines()[-1])
    print("openwhisk", df3["turn-round time"][:int(ratio*len(df1))].mean())

    print("sfs", df4["turn-round time"][:int(ratio*len(df1))].mean())


# 提取第三列数据
column_data_1 = df1.iloc[:, -1].values
column_data_2 = df2.iloc[:, -1].values
column_data_3 = df3.iloc[:, -1].values
column_data_4 = df4.iloc[:, -1].values

# 绘制这两个数组对应的 CDF 图
import matplotlib.pyplot as plt
import numpy as np

# 计算CDF
def compute_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

sorted_data_1, cdf_1 = compute_cdf(column_data_1)
sorted_data_2, cdf_2 = compute_cdf(column_data_2)
sorted_data_3, cdf_3 = compute_cdf(column_data_3)
sorted_data_4, cdf_4 = compute_cdf(column_data_4)

# 绘制CDF图
plt.figure(figsize=(10, 6))
plt.plot(sorted_data_1, cdf_1, label='Synergy')
plt.plot(sorted_data_2, cdf_2, label='OpenFaaS')
plt.plot(sorted_data_3, cdf_3, label='OpenWhisk')
plt.plot(sorted_data_4, cdf_4, label='SFS')

plt.xlabel('Turnaround Time')
plt.ylabel('CDF')
plt.title('Turnaround Time CDF Comparison')
plt.legend()
plt.grid(True)
# plt.show()

plt.savefig("./pdf/output.pdf")
