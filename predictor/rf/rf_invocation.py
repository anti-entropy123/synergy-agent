import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import time
from typing import List
from scipy.signal import periodogram
from statsmodels.tsa.stattools import acf, pacf
import scipy.fftpack

from qps_data_loader.loader import read_data, pw_zq_func_id, zq_tf_func_id, tf_zq_func_id, calc_error_rate, save_result


def compute_periodicity_strength(time_series, sampling_rate=1):
    """
    计算时间序列的周期性强度
    :param time_series: 1D NumPy 数组，表示时序数据
    :param sampling_rate: 采样率（时间步长），默认为1
    :return: 周期性强度 (0~1之间)，值越高代表周期性越强
    """
    # 计算功率谱密度 (PSD)
    freqs, power = periodogram(time_series, fs=sampling_rate)

    # 计算总能量
    total_power = np.sum(power)

    if total_power == 0:
        return 0  # 避免除零错误

    # 取最大峰值对应的频率成分能量（排除直流分量 freq=0）
    periodic_power = np.max(power[1:])

    # 计算周期性强度
    periodicity_strength = periodic_power / total_power

    return periodicity_strength


def coefficient_of_variation(data):
    """
    计算变异系数（CV）

    参数:
    - data: 1D NumPy 数组或列表

    返回:
    - CV: 变异系数
    """
    data = np.array(data)
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)  # 使用 ddof=1 计算样本标准差

    if mean == 0:
        return np.nan  # 避免除以 0，返回 NaN

    return std_dev / mean


def compute_acf_pacf(time_series, lags=6):
    """
    计算时间序列的 ACF 和 PACF
    :param time_series: 1D NumPy 数组，表示时序数据
    :param lags: 计算 ACF/PACF 的最大滞后阶数
    :return: ACF/PACF 特征数组
    """
    acf_values = acf(time_series, nlags=lags, fft=True)[:lags+1]
    pacf_values = pacf(time_series, nlags=lags)[:lags+1]
    return acf_values[1:], pacf_values[1:]  # 去掉 lag=0 的自相关


def compute_fft_features(time_series, top_k=5, sampling_rate=1):
    """
    计算时序数据的前 K 个最强频率和对应幅度
    :param time_series: 1D NumPy 数组，表示时序数据
    :param top_k: 选取前 K 个频率
    :param sampling_rate: 采样率（时间步长），默认为 1
    :return: 前 K 个频率 & 幅度
    """
    N = len(time_series)
    fft_values = scipy.fftpack.fft(time_series)
    freqs = np.fft.fftfreq(N, d=sampling_rate)

    # 取正频率部分
    pos_mask = freqs > 0
    freqs, power = freqs[pos_mask], np.abs(fft_values[pos_mask])

    # 选取前 K 个最大峰值对应的频率
    top_indices = np.argsort(power)[-top_k:][::-1]
    top_freqs = freqs[top_indices]
    top_amplitudes = power[top_indices]

    return top_freqs, top_amplitudes


def compute_burstiness_index(time_series):
    """
    计算突发指数（Burstiness Index）
    :param time_series: 1D NumPy 数组，表示时序数据
    :return: Burstiness Index
    """
    mean_val = np.mean(time_series)
    std_val = np.std(time_series, ddof=1)

    if mean_val + std_val == 0:
        return np.nan  # 避免除以零

    return (std_val - mean_val) / (std_val + mean_val)


def compute_peak_ratio(time_series):
    """
    计算峰值比率（Peak Ratio）
    :param time_series: 1D NumPy 数组，表示时序数据
    :return: 峰值比率
    """
    mean_val = np.mean(time_series)
    max_val = np.max(time_series)

    if mean_val == 0:
        return np.nan  # 避免除零错误

    return max_val / mean_val

from scipy.stats import skew, kurtosis

def compute_kurtosis_skewness(time_series):
    """
    计算时间序列的峰度和偏度

    参数:
    - time_series: 1D NumPy 数组，表示时序数据

    返回:
    - kurtosis_value: 峰度值
    - skewness_value: 偏度值
    """
    kurtosis_value = kurtosis(time_series, fisher=False)  # Fisher 参数设为 False 以得到 Pearson 峰度
    skewness_value = skew(time_series)
    return kurtosis_value, skewness_value

def comp_input(X: List):
    result = []

    for x in X:
        new_x = list(x[-60:])

        new_x += list(x[-1440:-1440+60])

        max_qps = max(x)
        min_qps = min(x)
        new_x += [max_qps, min_qps, max_qps-min_qps]

        mean_5 = sum(x[-5:])/5
        mean_10 = sum(x[-10:])/10
        mean_50 = sum(x[-50:])/50
        mean_200 = sum(x[-200:])/200
        mean_500 = sum(x[-500:])/500
        mean_1000 = sum(x[-1000:])/1000
        mean_1440 = sum(x[-1440:])/1440
        new_x += [mean_5, mean_10, mean_50, mean_200,
                  mean_500, mean_1000, mean_1440]

        diff_5 = x[-1] - x[-5]
        diff_10 = x[-1] - x[-10]
        diff_50 = x[-1] - x[-50]
        diff_100 = x[-1] - x[-100]
        diff_500 = x[-1] - x[-500]
        diff_1000 = x[-1] - x[-1000]
        diff_1440 = x[-1] - x[-1440]
        new_x += [diff_5, diff_10, diff_50, diff_100,
                  diff_500, diff_1000, diff_1440]

        std_5 = np.std(x[-5:])
        std_10 = np.std(x[-10:])
        std_50 = np.std(x[-50:])
        std_100 = np.std(x[-100:])
        std_500 = np.std(x[-500:])
        std_1000 = np.std(x[-1000:])
        std_1440 = np.std(x[-1440:])
        new_x += [std_5, std_10, std_50, std_100,
                  std_500, std_1000, std_1440]

        last_60 = x[-1-60]
        last_120 = x[-1-120]
        last_180 = x[-1-180]
        last_240 = x[-1-240]
        last_300 = x[-1-300]
        last_360 = x[-1-360]
        new_x += [last_60, last_120, last_180, last_240, last_300, last_360]

        new_x.append(compute_periodicity_strength(x, sampling_rate=1))
        new_x.append(coefficient_of_variation(x))

        acf_vals, pacf_vals = compute_acf_pacf(x)
        new_x += acf_vals.tolist()
        new_x += pacf_vals.tolist()

        fft_freqs, fft_amplitudes = compute_fft_features(x)
        new_x += fft_freqs.tolist()
        new_x += fft_amplitudes.tolist()

        new_x.append(compute_burstiness_index(x))
        new_x.append(compute_peak_ratio(x))

        kurtosis, skewness = compute_kurtosis_skewness(x)
        new_x += [kurtosis, skewness]

        result.append(new_x) 

    return result
    # return X


features_name = [f"x_{-i}" for i in range(-60, 0)] + \
    [f"x_{-i}" for i in range(-1440, -1440+60)] + \
    ["最大", "最小", "极差",
     "mean_5", "mean_10", "mean_50", "mean_200", "mean_500", "mean_1000", "mean_1440",
     "diff_5", "diff_10", "diff_50", "diff_100", "diff_500", "diff_1000", "diff_1440",
     "std_5", "std_10", "std_50", "std_100", "std_500", "std_1000", "std_1440",
     "last_60", "last_120", "last_180", "last_240", "last_300", "last_360",
     "周期强度", "变异系数"] + \
    [f"自相关系数_{i}" for i in range(6)] + [f"偏自相关系数_{i}" for i in range(6)] + \
    [f"fft频率_{i}" for i in range(5)] + \
    [f"fft幅度_{i}" for i in range(5)] + \
    ["突发指数", "峰值比率"] + \
    ["峰度", "偏度"]

# features_name = [f"x_{-i}" for i in range(-1440, 0)]


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

    X, y = np.array(comp_input(X)), np.array(y)
    # X.shape = (8560, 1440), y.shape = (8560, )
    print(f"数据集形状：X={X.shape}, y={y.shape}")

    # ========== 3. 划分训练集和测试集 ==========
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False)

    # ========== 4. 训练随机森林回归模型 ==========
    train_start = time.time()
    model = RandomForestRegressor(
        n_estimators=350, min_samples_split=14, min_samples_leaf=4, max_depth=30, bootstrap=True, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    train_time = time.time() - train_start

    importances = model.feature_importances_
    sorted_indices = np.argsort(importances)[::-1]  # 按重要性降序排序
    for idx in sorted_indices:
        if importances[idx] < 0.001:
            continue

        print(f"    {features_name[idx]}: {importances[idx]:.4f}")

    # ========== 5. 预测并反归一化 ==========
    pred_start = time.time()
    y_pred = model.predict(X_test)
    pred_time = time.time() - pred_start

    y_pred = scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()  # 反归一化
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    return y_test_actual, y_pred, train_time, pred_time


def randomized_search(data):
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

    X, y = np.array(comp_input(X)), np.array(y)

    param_distributions = {
        "n_estimators": np.arange(50, 500, 50),  # 50 ~ 500 棵树
        "max_depth": [None, 10, 20, 30, 40, 50],  # 最大深度
        "min_samples_split": np.arange(2, 20, 2),  # 节点最小样本数
        "min_samples_leaf": np.arange(1, 10, 1),  # 叶子节点最小样本数
        "max_features": ['sqrt', 'log2', None],  # 选择特征的比例
        "bootstrap": [True, False]  # 是否使用自助采样
    }

    from sklearn.model_selection import RandomizedSearchCV

    rf = RandomForestRegressor(random_state=42)
    random_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_distributions,
        n_iter=20,  # 迭代搜索 20 组参数
        cv=5,  # 5 折交叉验证
        scoring="neg_mean_squared_error",  # 评价指标：MSE
        verbose=2,
        random_state=42,
        n_jobs=-1  # 并行计算
    )

    random_search.fit(X, y)

    # 输出最佳参数
    print("最佳参数:", random_search.best_params_)


func_to_qps = read_data()


def test_rf(func_label, func_id):
    print(f"begin rf_{func_label}")
    actual, predict, t_time, p_time = train_and_predict(func_to_qps[func_id])
    print(t_time, p_time)
    save_result(f"rf_{func_label}", predict, actual)
    calc_error_rate(f"rf_{func_label}", actual, predict)


test_rf("pw_zq", pw_zq_func_id)
test_rf("zq_tf", zq_tf_func_id)
test_rf("tf_zq", tf_zq_func_id)

# randomized_search(func_to_qps[pw_zq_func_id])
