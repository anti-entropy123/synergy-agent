#!/usr/bin/python3

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 手动指定中文字体
# plt.rcParams["font.family"] = fm.FontProperties(fname="/usr/share/fonts/truetype/wqy/").get_name()
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei', 'SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

trace = "hw"
hw_sg_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_burst/result/agent1_8.csv').iloc[:, -1].values)
hw_sgf_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_force_CDF_{trace}_500_burst/result/agent1_8.csv').iloc[:, -1].values)  
hw_of_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values) 
hw_ow_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values)
hw_sfs_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values)  

trace = "wr"
wr_sg_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_CDF_{trace}_500_burst/result/agent1_8.csv').iloc[:, -1].values)
wr_sgf_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_Synergy_force_CDF_{trace}_500_burst/result/agent1_8.csv').iloc[:, -1].values)
wr_of_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenFaaS_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values) 
wr_ow_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_OpenWhisk_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values)
wr_sfs_trace = np.sort(pd.read_csv(f'./synergy-controller/export/result_SFS_CDF_{trace}_500_burst/result/agent21_28.csv').iloc[:, -1].values)


print(len(hw_sg_trace), len(hw_of_trace), len(hw_ow_trace), len(hw_sfs_trace), len(hw_sgf_trace), len(wr_sg_trace), len(wr_of_trace), len(wr_ow_trace), len(wr_sfs_trace), len(wr_sgf_trace))

with open('./synergy-controller/export-500/sec4_burst_archive.csv', 'w') as f:
    f.write('hw_sg, hw_of, hw_ow, hw_sfs, hw_sgf, wr_sg, wr_of, wr_ow, wr_sfs, wr_sgf\n')

    for i in range(len(hw_sg_trace)):
        f.write(f'{hw_sg_trace[i]},{hw_of_trace[i]},{hw_ow_trace[i]},{hw_sfs_trace[i]},{hw_sgf_trace[i]},{wr_sg_trace[i]},{wr_of_trace[i]},{wr_ow_trace[i]},{wr_sfs_trace[i]},{wr_sgf_trace[i]}\n')
     

# 创建图形和子图
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# 绘制华为trace的CDF图
axes[0].plot(hw_sg_trace, np.arange(1, len(hw_sg_trace) + 1) / len(hw_sg_trace), label='Synergy')
axes[0].plot(hw_of_trace, np.arange(1, len(hw_of_trace) + 1) / len(hw_of_trace), label='OpenFaaS')
axes[0].plot(hw_ow_trace, np.arange(1, len(hw_ow_trace) + 1) / len(hw_ow_trace), label='OpenWhisk')
axes[0].plot(hw_sfs_trace, np.arange(1, len(hw_sfs_trace) + 1) / len(hw_sfs_trace), label='SFS')
axes[0].plot(hw_sgf_trace, np.arange(1, len(hw_sg_trace) + 1) / len(hw_sg_trace), label='Synergy-P')

axes[0].set_xlabel('(a) 华为函数执行持续时间')
axes[0].set_ylabel('经验累积分布函数(CDF)')
axes[0].legend(loc=(0., 1.), ncol=5, frameon=False, handlelength=1, handletextpad=0.5, columnspacing=1.5)


# 绘制微软trace的CDF图
axes[1].plot(wr_sg_trace, np.arange(1, len(wr_sg_trace) + 1) / len(wr_sg_trace))
axes[1].plot(wr_of_trace, np.arange(1, len(wr_of_trace) + 1) / len(wr_of_trace))
axes[1].plot(wr_ow_trace, np.arange(1, len(wr_ow_trace) + 1) / len(wr_ow_trace))
axes[1].plot(wr_sfs_trace, np.arange(1, len(wr_sfs_trace) + 1) / len(wr_sfs_trace))
axes[1].plot(wr_sgf_trace, np.arange(1, len(wr_sgf_trace) + 1) / len(wr_sgf_trace))

# axes[1].set_title('微软Trace请求周转时间CDF')
axes[1].set_xlabel('(b) 微软函数执行持续时间')
# axes[1].set_ylabel('累积分布')

# 两个子图都显示网格
for ax in axes:
    ax.grid(ls="--", color="#D0D0D0", zorder=-2)
    ax.set_xscale('log')
    # ax.set_xlim(10,)

# plt.tight_layout()
plt.subplots_adjust(hspace=0.6, wspace=0.20, top=0.84, bottom=0.18, left=0.1, right=0.95)

plt.savefig("./pdf/sec4_cdf.pdf")
