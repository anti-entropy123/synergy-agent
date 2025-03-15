#!/usr/bin/python3

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei','SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

trace = "hw"
hw_sg_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_luan_poisson/result/agent1_8.csv').iloc[:, -1].values)
hw_of_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values) 
hw_ow_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values)
hw_sfs_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values)  

trace = "wr"
wr_sg_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_luan_poisson/result/agent1_8.csv').iloc[:, -1].values)
wr_of_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values) 
wr_ow_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values)
wr_sfs_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv').iloc[:, -1].values)

# 创建图形和子图
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

hw_sg_avg = []
hw_of_avg = []
hw_ow_avg = []
hw_sfs_avg = []

wr_sg_avg = []
wr_of_avg = []
wr_ow_avg = []
wr_sfs_avg = []

length = len(hw_sg_trace)

for ratio in range(50, 101, 10):
    ratio /= 100
    hw_sg_avg.append(hw_sg_trace[:int(ratio*length)].mean())
    hw_of_avg.append(hw_of_trace[:int(ratio*length)].mean())
    hw_ow_avg.append(hw_ow_trace[:int(ratio*length)].mean())
    hw_sfs_avg.append(hw_sfs_trace[:int(ratio*length)].mean())

    wr_sg_avg.append(wr_sg_trace[:int(ratio*length)].mean())
    wr_of_avg.append(wr_of_trace[:int(ratio*length)].mean())
    wr_ow_avg.append(wr_ow_trace[:int(ratio*length)].mean())
    wr_sfs_avg.append(wr_sfs_trace[:int(ratio*length)].mean())

    print("百分位:", ratio)
    print("hw:", hw_sg_avg[-1], hw_of_avg[-1], hw_ow_avg[-1], hw_sfs_avg[-1])
    print("wr:", wr_sg_avg[-1], wr_of_avg[-1], wr_ow_avg[-1], wr_sfs_avg[-1])

# 画若干组柱状图, 每组的x轴刻度分别为 P50, P60 ... P90. 
# 每组内的若干柱子, 需要彼此不重叠, 且柱子宽度相同
# 设置柱状图的宽度
bar_width = 1.5
line_width = 0.1

# 设置柱状图的x轴位置
index = np.arange(50, 101, 10)

# 绘制柱状图
axes[0].bar(index - 1.5*bar_width, hw_sg_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="Synergy")
axes[0].bar(index - 0.5*bar_width, hw_of_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="OpenFaaS")
axes[0].bar(index + 0.5*bar_width, hw_ow_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="OpenWhisk")
axes[0].bar(index + 1.5*bar_width, hw_sfs_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="SFS")
axes[0].set_xlabel("(a) 华为函数")
axes[0].set_ylabel("平均周转时间(ms)")
# axes[0].set_title("Hardware")
axes[0].set_xticks(index)
axes[0].set_xticklabels([f"P{p}" for p in range(50, 101, 10)])

axes[0].legend(loc=(0., 1.02), ncol=4, frameon=False )

# 绘制柱状图
# 设置柱状图的边框宽度
axes[1].bar(index - 1.5*bar_width, wr_sg_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="Synergy")
axes[1].bar(index - 0.5*bar_width, wr_of_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="OpenFaaS")
axes[1].bar(index + 0.5*bar_width, wr_ow_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="OpenWhisk")
axes[1].bar(index + 1.5*bar_width, wr_sfs_avg, bar_width, linewidth=line_width, zorder=10, edgecolor="black", label="SFS")
axes[1].set_xlabel("(b) 微软函数")
# axes[1].set_ylabel("平均周转时间(ms)")
# axes[1].set_title("Hardware")
axes[1].set_xticks(index)
axes[1].set_xticklabels([f"P{p}" for p in range(50, 101, 10)])

for ax in axes:
    ax.grid(ls="--", color="#D0D0D0", zorder=-2,)

plt.subplots_adjust(hspace=0.6, wspace=0.20, top=0.84, bottom=0.2, left=0.1, right=0.95)

plt.savefig("pdf/sec3_percentage_avg.pdf")