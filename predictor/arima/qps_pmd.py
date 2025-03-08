import time
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm

from qps_data_loader.loader import read_data, pw_zq_func_id, zq_tf_func_id, tf_zq_func_id, calc_error_rate, save_result

# long_col_id = set([37, 38, 88, 89, 91, 92, 93, 104, 125, 126, 127, 130, 132, 149, 155, 156, 165, 
#                    166, 167, 168, 170, 171, 172, 173, 174, 175, 179, 194])
# # long_col_id = set([4, 5, 6])
# short_col_id = list(filter(lambda x: not x in long_col_id, range(200)))

# print(long_col_id)
# print(short_col_id)


def train_and_predict(data):
    # 读取数据
    # data = data.iloc[:3000, :]  # 取前 3000 行
    time_len = len(data)

    # 选择第 190 个函数的调用数据
    # print(data)
    # ts_long = data.iloc[:, [i+2 for i in list(short_col_id)]].sum(axis=1).to_frame("long_sum")
    # ts = pd.array(data=data)
    ts = pd.Series(data, index=pd.date_range(start="2012-03-01", periods=time_len, freq="1min"))

    print(ts)
    # index = pd.date_range('2012-03-01', periods=time_len, freq='1min')  # 设置时间索引
    # ts.index = index

    # 划分训练集和测试集
    train_size = int(time_len * 0.8)
    train_ts, test_ts = ts[:train_size], ts[train_size:]

    # 训练 ARIMA 模型（记录耗时）
    start_train = time.time()
    auto_model = pm.auto_arima(train_ts, seasonal=False, stepwise=True, trace=True)

    # 获取最佳阶数
    p, d, q = auto_model.order
    # p, d, q = 5, 2, 3
    print(f"最佳 ARIMA 阶数: p={p}, d={d}, q={q}")

    # 重新拟合 ARIMA 模型
    model = ARIMA(train_ts.astype(float), order=(p, d, q))
    proper_model = model.fit()
    train_time = time.time() - start_train  # 计算训练耗时

    predict = []
    # 进行预测（记录耗时）
    start_pred = time.time()
    new_model = proper_model.append(test_ts, refit=False)
    predict = new_model.predict(start=test_ts.index[0], end=test_ts.index[-1], dynamic=False)
    pred_time = time.time() - start_pred  # 计算预测耗时

    return test_ts, predict, train_time, pred_time


func_to_qps = read_data()

def test_arima(func_label, func_id):
    print(f"begin arima_{func_label}")
    actual, predict, t_time, p_time = train_and_predict(func_to_qps[func_id])
    print(t_time, p_time)
    save_result(f'arima_{func_label}', predict, actual)
    calc_error_rate("arima_pw_zq", actual, predict)


test_arima("pw_zq", pw_zq_func_id)
test_arima("zq_tf", pw_zq_func_id)
test_arima("tf_zq", pw_zq_func_id)