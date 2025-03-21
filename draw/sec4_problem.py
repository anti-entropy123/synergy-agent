import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
import matplotlib.font_manager as fm

# 手动指定中文字体
plt.rcParams["font.family"] = ['WenQuanYi Micro Hei','SimSun', 'Arial']
# plt.rcParams["font.family"] = "SimSun"
plt.rcParams.update({'font.size': 18})

# 设置字体和图形参数
# mpl.rcParams["font.family"] = 'Nimbus Sans'
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

methods = ["100%", "75%", "50%", "25%", "0%"]

# 数据
ffff = [5119.55, 5565.35, 9539.51]
fffc = [5579.08, 5983.14, 9713.32]
ffcc = [5968.31, 7022.91, 10333.80]
fccc = [6802.12, 7722.42, 11489.15]
cccc = [7475.60, 7858.47, 11596.96]

all_lats1 = [ffff, fffc, ffcc, fccc, cccc]
# baseline = [i for i in ffcc]

# for lst in all_lats1:
#     for idx in range(len(ffcc)):
#         lst[idx] /= baseline[idx]

# 颜色设置
# back_colors = ['#08519C', '#DA70D6', '#4EEE94', '#FFA500', '#ff6600']
back_colors = ['#08306B', '#08519C', '#2171B5', '#6BAED6', '#C6DBEF']

fig, ax = plt.subplots(figsize=(9, 4), dpi=300)  # 创建一个子图，调整图形大小

# 设置子图间距和四周空白
plt.subplots_adjust(hspace=None, wspace=None, top=0.9,
                    bottom=0.12, left=0.18, right=0.82)

width = 0.17
gap = 0.00
group_gap = 1-width*5
# fontsize = 13

indexs = [i * (width * 5 + group_gap) - 2*width for i in range(3)]  # 每组之间的间隙

# 绘制柱状图
bars = []
for i in range(3):  # 只绘制三组
    bar_group = []
    for j, method in enumerate(methods):
        bar = ax.bar(indexs[i] + j * (width + gap), all_lats1[j][i], width=width, color=back_colors[j],
                     edgecolor="#000000", linewidth=0.5, zorder=2)
        bar_group.append(bar)
    bars.append(bar_group)

# 添加数据标签
# for i in range(3):
#     for j in range(5):
#         ax.text(indexs[i] + j * (width + gap), all_lats1[j][i] + max(max(all_lats1)) * 0.01,
#                 f'{round(all_lats1[j][i])}', ha='center', va='bottom', rotation=90)

ax.set_ylabel("平均周转时间(ms)", labelpad=2)

# 调整图例为横向两个
ax.legend([bars[0][i] for i in range(5)], methods, ncol=5, loc=(1, 1.05), bbox_to_anchor=(
    0.001, 0.999), frameon=False, handletextpad=0.3, columnspacing=1, handlelength=1.5)

# 设置 y 轴范围
ax.set_ylim(3200, max(max(ffff), max(fffc), max(
    ffcc), max(fccc), max(cccc)) * 1.08)
# ax.set_ylim(0.5, 1.5)

# 设置 x 轴刻度
plt.xticks([i for i in range(3)])
plt.xlim(-0.6, 2.6)
ax.set_xticklabels(["长函数多", "长短一致", "短函数多"])
ax.tick_params(axis='y')  # 设置 y 轴刻度标签字体大小

plt.savefig('pdf/sec4_problem.pdf',)
# plt.show()
