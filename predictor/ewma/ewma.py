import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from qps_data_loader.loader import read_data, pw_zq_func_id, zq_tf_func_id, tf_zq_func_id, calc_error_rate, save_result


def train_and_predict(data):
    time_series_length = 7 * 1440  # 7 天，每天 1440 分钟
    call_volume = np.array(data)  # 模拟调用量

    # 80% 训练集, 20% 测试集
    split_ratio = 0.8
    split_index = int(time_series_length * split_ratio)
    # train_data = call_volume[:split_index]
    # test_data = call_volume[split_index:]

    # 计算训练集的 EWMA
    alpha = 2 / (1440 + 1)  # 平滑因子
    # 预测测试集（使用训练集最后一个 EWMA 作为起点）
    
    prediction = []
    predict_start = time.time()

    for i in range(len(data) - split_index):
        train_ewma = pd.Series(call_volume[split_index+i-1440:split_index+i]).ewm(alpha=alpha, adjust=False).mean()
        prediction.append(train_ewma.iloc[-1])

    return np.array(prediction), call_volume[split_index:], 0, time.time() - predict_start

func_to_qps = read_data()

def test_ewma(func_label, func_id):
    print(f"begin ewma_{func_label}")
    predict, actual, t_time, p_time = train_and_predict(func_to_qps[func_id])
    print(t_time, p_time)
    # print(list(predict))
    # print(list(actual))
    save_result(f'ewma_{func_label}', predict, actual)
    calc_error_rate(f"ewma_{func_label}", predict, actual)

test_ewma("pw_zq", pw_zq_func_id)
test_ewma("zq_tf", zq_tf_func_id)
test_ewma("tf_zq", tf_zq_func_id)

# plt.plot(actual, label="actual", linestyle='--', zorder=10)
# plt.plot(predict, label="predict")

# plt.legend()
# plt.title("指数加权移动平均（EWMA）")
# plt.savefig("ewma/ewma_output.pdf")