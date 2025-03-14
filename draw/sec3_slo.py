import re

pattern = re.compile(r'\d+\.\d+')

labels = ['Synergy', 'OpenFaaS', 'OpenWhisk', 'SFS']

hw_slo_sg = []
hw_slo_of = []
hw_slo_ow = []
hw_slo_sfs = []

slo_hw = "./synergy-controller/export/sec3_slo_box_hw.log"
with open(slo_hw, "r") as f:
    lines = f.read().strip().split("\n")
    for line in lines:
        # 用正则表达式匹配类似 12.0 的数据
        match = pattern.search(line)
        if match:
            value = float(match.group())
    
        if line.startswith('synergy'):
            hw_slo_sg.append(value)
        elif line.startswith('openfaas'):
            hw_slo_of.append(value)
        elif line.startswith('openwhisk'):
            hw_slo_ow.append(value)
        elif line.startswith('sfs'):
            hw_slo_sfs.append(value)

print(hw_slo_sg)
print(hw_slo_of)
print(hw_slo_ow)
print(hw_slo_sfs)

# 绘制箱形图
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
matplotlib.rcParams["font.family"] = ['WenQuanYi Micro Hei', 'SimSun', 'Arial']
plt.rcParams.update({'font.size': 22})

# 绘制箱形图
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

axes[0].boxplot([hw_slo_sg, hw_slo_of, hw_slo_ow, hw_slo_sfs], labels=labels, patch_artist=True)
axes[0].tick_params(axis='x', rotation=15)


axes[0].set_xlabel('华为函数数据')
axes[0].set_ylabel('SLO 违背率(%)')

wr_slo_sg = []
wr_slo_of = []
wr_slo_ow = []
wr_slo_sfs = []

slo_wr = "./synergy-controller/export/sec3_slo_box_wr.log"
with open(slo_wr, "r") as f:
    lines = f.read().strip().split("\n")
    for line in lines:
        # 用正则表达式匹配类似 12.0 的数据
        match = pattern.search(line)
        if match:
            value = float(match.group())
    
        if line.startswith('synergy'):
            wr_slo_sg.append(value)
        elif line.startswith('openfaas'):
            wr_slo_of.append(value)
        elif line.startswith('openwhisk'):
            wr_slo_ow.append(value)
        elif line.startswith('sfs'):
            wr_slo_sfs.append(value)

axes[1].boxplot([wr_slo_sg, wr_slo_of, wr_slo_ow, wr_slo_sfs], labels=labels, patch_artist=True)
axes[1].set_xlabel('微软函数数据')
axes[1].tick_params(axis='x', rotation=15)
# axes[1].set_ylabel('SLO 违背率')

for ax in axes:
    ax.grid(ls="--", color="#D0D0D0", zorder=-2)
    # ax.set_xscale('log')
    # ax.set_xlim(10,)

plt.subplots_adjust(hspace=0.6, wspace=0.15, top=0.95, bottom=0.25, left=0.08, right=0.98)
plt.savefig('pdf/sec3_slo_box.pdf')
