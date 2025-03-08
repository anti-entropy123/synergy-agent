import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import json

# 生成模拟时间序列数据（7天的分钟级调用量）
time_steps = 7 * 1440  # 7天，每天1440分钟

# pw_zq_func_id = '5315be05fc3b21a3f483ed0759bce825764dcf8a762623a1d94ff63f9d9ce4cc'
pw_zq_func_id = '4fec01ac4ad62bb7fdff5851257d9a097af424ae03ba62c0e94167e3d5e24ef6'
zq_tf_func_id = '660323aa6f1012c8eca3c7d8153cb436320b48ed84f82bf3e816b494ad8dfde2'
tf_zq_func_id = 'f8c5d1ba78b7d2f4d2d2a0d8bbc31f0b93185edce1d0788fbc362f22bd931af2'

def read_data():
    func_to_qps = {}
    func_to_qps[pw_zq_func_id] = []
    func_to_qps[zq_tf_func_id] = []
    func_to_qps[tf_zq_func_id] = []

    file_pattern = "azure_data/az_hot_func_invocation_day_{:02d}.csv"
    invoc_nums = []
    for i in range(7):
        file_name = file_pattern.format(i)
        df = pd.read_csv(file_name, delimiter=",")
        for line in df[:].iterrows():
            fid = line[1]["HashFunction"]
            if fid not in func_to_qps:
                continue
            
            for seq in range(1440):
                func_to_qps[fid].append(line[1][str(seq+1)])

    return func_to_qps


def calc_error_rate(name, test_ts, predict):
    # 计算 MAPE（避免 0 除错误）
    def mean_absolute_percentage_error(y_true, y_pred): 
        # 将输入转换为一维数组
        y_true = np.array(y_true).flatten()
        y_pred = np.array(y_pred).flatten()
        nonzero_idx = y_true != 0  # 避免除以 0
        return np.mean(np.abs((y_true[nonzero_idx] - y_pred[nonzero_idx]) / y_true[nonzero_idx])) * 100
    
    # # === 计算误差 ===
    mse = mean_squared_error(test_ts, predict)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(test_ts, predict)
    r2 = r2_score(test_ts, predict)
    mape = mean_absolute_percentage_error(test_ts, predict)

    # # 打印评估指标
    print(f"{name} 预测的评估结果：")
    # print(f"MSE  (均方误差): {mse:.4f}")
    # print(f"RMSE (均方根误差): {rmse:.4f}")
    # print(f"MAE  (平均绝对误差): {mae:.4f}")
    # print(f"MAPE (平均绝对百分比误差): {mape:.2f}%")
    print(f"R²   (决定系数): {r2:.4f}")
    # print(f"训练耗时: {train_time:.4f} 秒")
    # print(f"预测耗时: {pred_time:.6f} 秒")
    # print(f"MAPE (平均绝对百分比误差): {mape:.4f}")

def save_result(prefix, predictions, y_test_actual):
    with open(f"./results/{prefix}_y_test_actual.json", "w") as f:
        f.write(json.dumps(y_test_actual.tolist()))

    with open(f"./results/{prefix}_predictions.json", "w") as f:
        f.write(json.dumps(predictions.tolist()))
