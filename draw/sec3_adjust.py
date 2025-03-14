import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.font_manager as fm

plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei', 'SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

# 示例数据
data1 = np.array([
    [80.79, 19.21],  # 场景1
    [43.89, 56.11],  # 场景2
    [68.07, 31.93],  # 场景3
])

data2 = np.array([
    [89.52, 10.48],  # 场景1
    [99.62,0.38 ],  # 场景2
    [93.32, 6.68],  # 场景3
])

# 分类标签
groupLabels = ["长函数多", "长短一致", "短函数多"]

# 绘制堆叠柱状图的函数
def plotBarStackGroups(ax, stackData, groupLabels, _ylabel, xlabel):
    nGroups = stackData.shape[0]
    barWidth = 0.3
    indices = np.arange(nGroups)
    
    # 绘制实际利用率的堆叠柱状图
    bar1_data = [i/100 for i in stackData[:, 0]]
    bars1 = ax.bar([i-barWidth/2 for i in indices], bar1_data, barWidth, label='负载感知', color='#08519C')
    # 在实际利用率上绘制虚拟利用率的堆叠柱状图
    bar2_data = [(x+y)/100 for x, y in zip(stackData[:, 0], stackData[:, 1]) ]
    bars2 = ax.bar([i+barWidth/2 for i in indices], bar2_data, barWidth, label='负载不感知', color='#9ECAE1',)
    
    ax.set_ylim([0, 1])
    ax.set_yticks([round(i, 1) for i in np.arange(0, 1.1, 0.2)])
    ax.set_yticklabels(ax.get_yticks())  # 设置纵坐标刻度的字体大小
    ax.set_xlim([-0.5, nGroups - 0.5])
    ax.set_xticks(indices)
    ax.set_xticklabels(groupLabels)
    ax.set_xlabel(xlabel, labelpad=10)  # 添加X轴标签
    
    return bars1, bars2

# 创建两个子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# 调整子图间距
fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.35, wspace=0.3)

# 绘制第一个子图
bars1_1, bars2_1 = plotBarStackGroups(ax1, data1, groupLabels, '时间占比()', '(a) 平均周转时间（归一化）')

# 绘制第二个子图
bars1_2, bars2_2 = plotBarStackGroups(ax2, data2, groupLabels, '时间占比(%)', '(b) 任务完成时间（归一化）')

# ax1.set_ylabel('', fontsize=8, labelpad=1)  # 减少标签与Y轴之间的距离
# 创建合并的图例
fig.legend([bars1_1, bars2_1], ['负载感知', '负载不感知'], loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=False)

plt.subplots_adjust(hspace=0.6, wspace=0.2, top=0.85, bottom=0.2, left=0.08, right=0.95)
# 保存图像
plt.savefig('pdf/sec3_adjust.pdf')
# plt.show()