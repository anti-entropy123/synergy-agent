import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import time

from qps_data_loader.loader import read_data, pw_zq_func_id, zq_tf_func_id, tf_zq_func_id, calc_error_rate, save_result


def train_and_predict(data):
    # ========== 1. 读取数据 ========== 
    # 假设你的数据是一个 numpy 数组，shape 为 (10080, )
    data = np.array(data)  # 这里 invoc_nums 代表你的调用量数据

    # 归一化数据
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data.reshape(-1, 1)).flatten()  # 归一化并展平

    # ========== 2. 创建时间序列特征 ==========
    window_size = 1440  # 过去1天（1440分钟）作为输入
    X, y = [], []

    for i in range(len(data_scaled) - window_size):
        X.append(data_scaled[i:i+window_size])  # 过去 1440 分钟作为特征
        y.append(data_scaled[i+window_size])    # 预测下一分钟的调用量

    X, y = np.array(X), np.array(y)
    print(f"数据集形状：X={X.shape}, y={y.shape}")  # X.shape = (8560, 1440), y.shape = (8560, )

    # ========== 3. 划分训练集和测试集 ==========
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # ========== 4. 训练随机森林回归模型 ==========
    train_start = time.time()
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    train_time = time.time() - train_start

    # ========== 5. 预测并反归一化 ==========
    pred_start = time.time()
    y_pred = model.predict(X_test)
    pred_time = time.time() - pred_start

    y_pred = scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()  # 反归一化
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    return y_test_actual, y_pred, train_time, pred_time

func_to_qps = read_data()

def test_rf(func_label, func_id):
    print(f"begin rf_{func_label}")
    predict, actual, t_time, p_time = train_and_predict(func_to_qps[pw_zq_func_id])
    print(t_time, p_time)
    save_result(f"rf_{func_label}", predict, actual)
    calc_error_rate(f"rf_{func_label}", predict, actual)

test_rf("pw_zq", pw_zq_func_id)
test_rf("zq_tf", zq_tf_func_id)
test_rf("tf_zq", tf_zq_func_id)

# print("begin ")
# func_id = zq_tf_func_id
# predict, actual = train_and_predict(func_to_qps[func_id])
# calc_error_rate(predict, actual)
# save_result('rf_zq_tf', predict, actual)

# print("begin ")
# func_id = tf_zq_func_id
# predict, actual = train_and_predict(func_to_qps[func_id])
# calc_error_rate(predict, actual)
# save_result('rf_tf_zq', predict, actual)