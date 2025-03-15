#!/usr/bin/python3

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei','SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

# stage1. 中心控制器阶段; 
# stage2. (包含在1中) 排序窗口等待时间; 
# stage3. 节点运行阶段; 
# stage4. (包含在3中) cpu时间.

slo_ratio = 1.5

trace = "hw"
hw_sg_trace = pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_luan_poisson/result/agent1_8.csv')
hw_sg_stage1 = hw_sg_trace['t1-t0'].mean()
hw_sg_stage2 = 7.5
hw_sg_stage3 = hw_sg_trace['t2-t1'].mean()
hw_sg_stage4 = hw_sg_trace['cpu time'].mean()


hw_of_trace = pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
hw_of_stage1 = hw_of_trace['t1-t0'].mean()
hw_of_stage2 = 0
hw_of_stage3 = hw_of_trace['t2-t1'].mean()
hw_of_stage4 = hw_of_trace['cpu time'].mean()


hw_ow_trace = pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
hw_ow_stage1 = hw_ow_trace['t1-t0'].mean()
hw_ow_stage2 = 0
hw_ow_stage3 = hw_ow_trace['t2-t1'].mean()
hw_ow_stage4 = hw_ow_trace['cpu time'].mean()


hw_sfs_trace = pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
hw_sfs_stage1 = hw_sfs_trace['t1-t0'].mean()
hw_sfs_stage2 = 0
hw_sfs_stage3 = hw_sfs_trace['t2-t1'].mean()
hw_sfs_stage4 = hw_sfs_trace['cpu time'].mean()

trace = "wr"
wr_sg_trace = pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_luan_poisson/result/agent1_8.csv')
wr_sg_stage1 = wr_sg_trace['t1-t0'].mean()
wr_sg_stage2 = 7.5
wr_sg_stage3 = wr_sg_trace['t2-t1'].mean()
wr_sg_stage4 = wr_sg_trace['cpu time'].mean()

wr_of_trace = pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
wr_of_stage1 = wr_of_trace['t1-t0'].mean()
wr_of_stage2 = 0
wr_of_stage3 = wr_of_trace['t2-t1'].mean()
wr_of_stage4 = wr_of_trace['cpu time'].mean()

wr_ow_trace = pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
wr_ow_stage1 = wr_ow_trace['t1-t0'].mean()
wr_ow_stage2 = 0
wr_ow_stage3 = wr_ow_trace['t2-t1'].mean()
wr_ow_stage4 = wr_ow_trace['cpu time'].mean()

wr_sfs_trace = pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_luan_poisson/result/agent21_28.csv')
wr_sfs_stage1 = wr_sfs_trace['t1-t0'].mean()
wr_sfs_stage2 = 0
wr_sfs_stage3 = wr_sfs_trace['t2-t1'].mean()
wr_sfs_stage4 = wr_sfs_trace['cpu time'].mean()


print('hw_sg', hw_sg_stage1, hw_sg_stage2, hw_sg_stage3, hw_sg_stage4)
print('hw_of', hw_of_stage1, hw_of_stage2, hw_of_stage3, hw_of_stage4)
print('hw_ow', hw_ow_stage1, hw_ow_stage2, hw_ow_stage3, hw_ow_stage4)
print('hw_sfs', hw_sfs_stage1, hw_sfs_stage2, hw_sfs_stage3, hw_sfs_stage4)
print('wr_sg', wr_sg_stage1, wr_sg_stage2, wr_sg_stage3, wr_sg_stage4)
print('wr_of', wr_of_stage1, wr_of_stage2, wr_of_stage3, wr_of_stage4)
print('wr_ow', wr_ow_stage1, wr_ow_stage2, wr_ow_stage3, wr_ow_stage4)
print('wr_sfs', wr_sfs_stage1, wr_sfs_stage2, wr_sfs_stage3, wr_sfs_stage4)

# 创建图形和子图
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# 画横向的堆叠柱状图, 将 hw_sg_stage1 到 stage4 画在一个柱子上. 

width = 0.35  # the width of the bars
default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
lw = 0.5

labels = ['中心控制器', '窗口等待时间', '节点运行', 'CPU时间']

# Synergy
x = [3]
axes[0].barh(x, hw_sg_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sg_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sg_stage3, width, left=hw_sg_stage1, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sg_stage4, width, left=hw_sg_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# OpenFaaS
x = [2]
axes[0].barh(x, hw_of_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_of_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_of_stage3, width, left=hw_of_stage1+hw_of_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_of_stage4, width, left=hw_of_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# OpenWhisk 
x = [1]
axes[0].barh(x, hw_ow_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_ow_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_ow_stage3, width, left=hw_ow_stage1+hw_ow_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_ow_stage4, width, left=hw_ow_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# SFS
x = [0]
axes[0].barh(x, hw_sfs_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sfs_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sfs_stage3, width, left=hw_sfs_stage1+hw_sfs_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[0].barh(x, hw_sfs_stage4, width, left=hw_sfs_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

axes[0].set_xlabel('华为函数分阶段耗时（ms）')
# axes[0].set_title('Time Breakdown by Stage')
axes[0].set_yticks([0, 1, 2, 3])
# 设置 x 轴刻度为['SFS', 'OpenWhisk', 'OpenFaaS', 'Synergy']
axes[0].set_yticklabels(['SFS', 'OpenWhisk', 'OpenFaaS', 'Synergy'])
axes[0].legend()
# 绘制四个 legend 条目, 它们的样式分别是 1. 橙色(无hatch) 2. 橙色(有hatch) 3. 绿色(无hatch) 4. 绿色(有hatch)

# Customize legend handles to ensure correct styling
handles, labels = axes[0].get_legend_handles_labels()
axes[0].legend(loc=(0, 1.02), handles=handles[:4], labels=labels, ncol=4, frameon=False, handlelength=1, handletextpad=0.5,)


# 模仿上面的代码, 将 wr 的数据绘制到 axes[1] 上.

# Synergy
x = [3]
axes[1].barh(x, wr_sg_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sg_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sg_stage3, width, left=wr_sg_stage1, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sg_stage4, width, left=wr_sg_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# OpenFaaS
x = [2]
axes[1].barh(x, wr_of_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_of_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_of_stage3, width, left=wr_of_stage1+wr_of_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_of_stage4, width, left=wr_of_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# OpenWhisk 
x = [1]
axes[1].barh(x, wr_ow_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_ow_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_ow_stage3, width, left=wr_ow_stage1+wr_ow_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_ow_stage4, width, left=wr_ow_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

# SFS
x = [0]
axes[1].barh(x, wr_sfs_stage1, width, label=labels[0], color=default_colors[0], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sfs_stage2, width, left=0, label=labels[1], color=default_colors[0], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sfs_stage3, width, left=wr_sfs_stage1+wr_sfs_stage2, label=labels[2], color=default_colors[1], edgecolor='black', linewidth=lw, zorder=10)
axes[1].barh(x, wr_sfs_stage4, width, left=wr_sfs_stage1, label=labels[3], color=default_colors[1], hatch='xx', edgecolor='black', linewidth=lw, zorder=10)

axes[1].set_xlabel('微软函数分阶段耗时（ms）')
# axes[1] 不显示任何刻度标签
axes[1].set_yticks([])

# axes[1].set_title('Time Breakdown by Stage')
# axes[1].set_yticks([0, 1, 2, 3])
# 设置 x 轴刻度为['SFS', 'OpenWhisk', 'OpenFaaS', 'Synergy']
# axes[1].set_yticklabels(['SFS', 'OW', 'OF', 'SG'])

for ax in axes:
    ax.grid(ls="--", color="#D0D0D0", zorder=-2,)

plt.subplots_adjust(hspace=0.6, wspace=0.20, top=0.84, bottom=0.2, left=0.15, right=0.95)

plt.savefig("./pdf/sec3_breakdown.pdf")
