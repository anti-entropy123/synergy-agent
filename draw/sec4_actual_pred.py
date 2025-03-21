
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei', 'SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

methods = ['RF', 'LSTM', 'ARIMA'][:1]

trace_types = ['pw_zq', 'zq_tf', 'tf_zq']
trace_type_name = ['平稳型', '周期型', '突发型']

scale = 1000

fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
datasizes = [[0, 40], [20, 200], [50, 170],]
lw = 2.5

# for i in range(len(axes)):
#     method = methods[i]
    
#     for trace_idx, trace_type in enumerate(trace_types):
#         with open(f"./predictor/results/{method.lower()}_{trace_type}_y_test_actual.json", "r") as f:
#             actual = json.load(f)[:datasize]

#         with open(f"./predictor/results/{method.lower()}_{trace_type}_predictions.json", "r") as f:
#             pred = json.load(f)[:datasize]

#         axes[i].plot(actual, label=trace_type_name[trace_idx], zorder=5, linewidth=lw)
#         axes[i].plot(pred, label=trace_type_name[trace_idx], linestyle='--', zorder=10, linewidth=lw)

def check_actual(trace_idx):
    all_actual = []
    trace_type = trace_types[trace_idx]
    datasize = datasizes[trace_idx]

    for method in methods:
        with open(f"./predictor/results/{method.lower()}_{trace_type}_y_test_actual.json", "r") as f:
            actual = np.array(json.load(f)[datasize[0]:datasize[1]]).flatten() / scale
            all_actual.append(actual)

    for i in range(1, len(all_actual)):
        vaild = [abs(all_actual[i][idx] - all_actual[i-1][idx]) < 0.01 for idx in range(datasize[1]-datasize[0])]
        if not min(vaild):
            raise Exception(f"{trace_type_name[trace_idx]} actual not equal: {methods[i]} and {methods[i-1]}")

    return all_actual[0].tolist()

for trace_idx, trace_type in enumerate(trace_types):
    actual = check_actual(trace_idx)
    datasize = datasizes[trace_idx]

    ax = axes[trace_idx]
    
    # y轴坐标值旋转90度
    # ax.set_yticks()
    ax.set_xlabel(f'({chr(ord("a") + trace_idx)}) {trace_type_name[trace_idx]}')
    ax.plot(actual, label='真实值', zorder=5, linewidth=lw)

    for method in methods:
        with open(f"./predictor/results/{method.lower()}_{trace_type}_predictions.json", "r") as f:
            pred = json.load(f)[datasize[0]:datasize[1]]

        ax.plot(np.array(pred) / scale, label=method, linestyle='--', zorder=10, linewidth=lw)

axes[0].set_ylim(0, 15000 / scale)
axes[0].set_ylabel("函数调用量（千次/分钟）")

axes[1].set_ylim(0, 120000 / scale)
axes[2].set_ylim(0, 15000 / scale)

for ax in axes:
    # ax.set_yscale('log')
    ax.grid(ls="--", color="#D0D0D0", zorder=-2)

axes[0].legend(loc=(0.8, 1.02), ncol=6, labels=['真实值', '随机森林模型预测值'], frameon=False)
plt.subplots_adjust(wspace=0.2, hspace=0.4, left=0.10, right=0.99, top=0.8, bottom=0.2)

plt.savefig("./pdf/sec4_actual_pred.pdf")