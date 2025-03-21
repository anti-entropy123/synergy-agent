import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import numpy as np

# 手动指定中文字体
plt.rcParams["font.family"] = ['WenQuanYi Micro Hei', 'SimSun', 'Arial']
plt.rcParams.update({'font.size': 11})

# 不同的进程名称
processes1 = ['FnE', 'FnD', 'FnC', 'FnB', 'FnA']
processes2 = ['FnE', 'FnD', 'FnC', 'FnB', 'FnA']
# processes3 = ['FnE', 'FnC', 'FnA', 'FnB', 'FnD']
processes3 = ['FnE', 'FnD', 'FnC', 'FnB', 'FnA']
processes_lists = [processes1, processes2, processes3]

# 三组不同的时间数据
data1 = {
    "wait_times": [190, 57, 39, 21, 0],
    "fifo_times": [130, 133, 18, 18, 22],
    "cfs_times": [0, 0, 0, 0, 0]
}

cpu_times = {chr(ord('A')+i): data1['fifo_times'][i] for i in range(5)}

data2 = {
    "wait_times": [0, 0, 0, 0, 0],
    "fifo_times": [0, 0, 0, 0, 0],
    "cfs_times": [320, 318, 104, 107, 85]
}

# processes3 = ['FnE', 'FnC', 'FnA', 'FnB', 'FnD']
# data3 = {
#     "wait_times": [93, 70, 46, 24, 1],
#     "fifo_times": [23, 21, 22, 17, 22],
#     "cfs_times": [192, 0, 0, 0, 295]
# }

data3 = {
    "wait_times": [93, 1, 70, 24, 46],
    "fifo_times": [23, 22, 21, 17, 22],
    "cfs_times": [192, 295, 0, 0, 0,]
}

# 数据集列表
datasets = [data1, data2, data3]
titles = ["(a) FIFO", "(b) CFS", "(c) SFS"]

# 条形宽度和颜色
bar_width = 0.6
colors = ['#EEEEEE', '#9ECAE1', '#08519C',]
labels = ['等待', 'FIFO', 'CFS']

# 创建图形对象
# fig = plt.figure(figsize=())
fig, axs = plt.subplots(2, 2, figsize=(6.7, 4.5))

# 创建 GridSpec 对象
# gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1], width_ratios=[1, 1, 1])

# 创建子图
ax1 = axs[0, 0]
ax2 = axs[0, 1]
# ax3 = axs[1, 0]

fig.delaxes(axs[1, 0])
fig.delaxes(axs[1, 1])

bottom = 0.1   # 子图底部位置（0.0 到 1.0）
width = 0.43    # 子图宽度
left = 0.5-width/2    # 子图左侧位置（0.0 到 1.0，0.5 是居中）
height = 0.35   # 子图高度
ax3 = fig.add_axes([left, bottom, width, height])

axes = [ax1, ax2, ax3]

# 遍历每个子图，并传入不同的数据和进程名称
for ax, data, title, processes in zip(axes, datasets, titles, processes_lists):
    wait_times = data["wait_times"]
    fifo_times = data["fifo_times"]
    cfs_times = data["cfs_times"]

    for i, (process, wait, fifo, cfs) in enumerate(zip(processes, wait_times, fifo_times, cfs_times)):
        ax.barh(process, wait, color=colors[0], edgecolor='black', height=bar_width, label=labels[0] if i == 0 else "",zorder=2)
        ax.barh(process, fifo, left=wait, color=colors[1], edgecolor='black', height=bar_width, label=labels[1] if i == 0 else "",zorder=2)
        ax.barh(process, cfs, left=wait+fifo, color=colors[0], edgecolor='black', height=bar_width, label=labels[2] if i == 0 else "",zorder=2)

        # 添加文字标签
        if not ax == ax2:
            if wait > 3:
                ax.text(wait / 2, process, str(wait), va='center', ha='center', color='black', zorder=50)
            if fifo > 3:
                ax.text(wait + fifo / 2, process, str(fifo), va='center', ha='center', color='black', zorder=50)
            if ax == ax1 and cfs > 3:
                ax.text(wait + fifo + cfs / 2, process, str(cfs), va='center', ha='center', color='black', zorder=50)
            elif ax == ax3 and cfs > 3:
                ax.text(wait + fifo + cfs + 20, process, str(cfs), va='center', ha='center', color='black', zorder=50)
        else:
            if cfs > 3:
                ax.text(wait + fifo + cfs + 20, process, str(cfs), va='center', ha='center', color='black', zorder=50)
        

    # 设定子图的 x 轴标签，并调整字体大小
    ax.set_xlabel(f'{title}执行过程耗时（ms）',)

    # 设置 x 轴刻度字体大小
    ax.tick_params(axis='x', )

    # 设置 y 轴刻度（确保它们和 processes 对应）
    ax.set_yticks(range(len(processes)))
    ax.set_yticklabels(processes,)

ax1.set_xlim(0, 350)
ax2.set_xlim(0, 380)
ax3.set_xlim(0, 360)

# 为 CFS 绘制等待时间
ts = 15
func_id_map = {
    0: 0,
    1: 1,
    2: 3,
    3: 2,
    4: 4,
}

proc_status = [1, 1, 1, 1, 1]


row = 0
cursor = 2

def next_schedule(row):
    if not sum(proc_status):
        return -1

    while True:
        row += 1
        if row >= 5:
            row = 0
        
        if proc_status[row]:
            return row

def comp_width(ts):
    return ts + (5-sum(proc_status)) * 3

while cursor < max(data2['cfs_times']):
    if row == -1:
        break

    if not proc_status[row]:
        row += 1
        continue

    func_id = func_id_map[4-row]
    # is_wait = wait_matrx[row][col]
    # is_wait = (col % row) == 0
    x = cursor
    if x > data2['cfs_times'][func_id]:
        proc_status[row] = 0
        row = next_schedule(row)
        continue

    width = comp_width(ts)
    right = x + width
    if right > data2['cfs_times'][func_id]:
        width = data2['cfs_times'][func_id] - x
        proc_status[row] = 0

    ax2.add_patch(plt.Rectangle((x, (func_id+0.025)-bar_width/2), width, bar_width-0.05, facecolor=colors[2], edgecolor='black', linewidth=1., zorder=30))
    cursor += width
    row = next_schedule(row)

ts = 15
row = 0
cursor = 93 + 23
data3 = {'cfs_times': [data3['cfs_times'][i] + data3['wait_times'][i] + data3['fifo_times'][i] for i in range(5)]}
# 为 SFS 绘制 CFS 调度过程
proc_status = [0, 0, 0, 1, 1]
func_id_map = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}

while cursor < max(data3['cfs_times']):
    if row == -1:
        break

    if not proc_status[row]:
        row += 1
        continue

    func_id = func_id_map[4-row]
    # is_wait = wait_matrx[row][col]
    # is_wait = (col % row) == 0
    x = cursor
    if x > data3['cfs_times'][func_id]:
        proc_status[row] = 0
        row = next_schedule(row)
        continue

    width = comp_width(ts)
    right = x + width
    if right > data3['cfs_times'][func_id]:
        width = data3['cfs_times'][func_id] - x
        proc_status[row] = 0

    ax3.add_patch(plt.Rectangle((x, (func_id+0.025)-bar_width/2), width, bar_width-0.05, facecolor=colors[2], edgecolor='black', linewidth=1., zorder=30))
    cursor += width
    row = next_schedule(row)
    

ax3.annotate(
    text='1',           # 标注文本
    xy=(1, 1.1),           # 箭头指向的点 (数据坐标)
    xytext=(-30, 1.4),             # 文本位置 (数据坐标)
    arrowprops=dict(
        arrowstyle='->',         # 箭头样式 (可以是 '->', '-|>', '<-', 等)
        color='black',
        lw=1.                     # 箭头宽度
    ),
    color='black'
)

# 在整个图的上方添加一个共享图例
# fig.legend(labels, loc='upper center', ncol=3, frameon=False,)

from matplotlib.lines import Line2D
handles = [Line2D([0], [0], color=color, lw=10) for color in colors]
axes[0].legend(loc=(0.6, 1.02), handles=handles[:3], labels=labels, ncol=len(colors), frameon=False)


for ax in axes:
    ax.grid(ls="--", color="#D0D0D0", zorder=-2)

# 调整布局
# plt.tight_layout()
plt.subplots_adjust(wspace=0.15, hspace=0.4, left=0.06, right=0.99, top=0.92, bottom=0.15)

# 保存为 PDF
plt.savefig('pdf/sec3_gant.pdf',)

# 显示图表
plt.show()
