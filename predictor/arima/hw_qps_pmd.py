import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

long_col_id = set([37, 38, 88, 89, 91, 92, 93, 104, 125, 126, 127, 130, 132, 149, 155, 156, 165, 
                   166, 167, 168, 170, 171, 172, 173, 174, 175, 179, 194])
# long_col_id = set([4, 5, 6])
short_col_id = list(filter(lambda x: not x in long_col_id, range(200)))

print(long_col_id)
print(short_col_id)

plt.rcParams['font.sans-serif'] = ['SimSun']

# 读取数据
data = pd.read_csv('./hw_data/day_000_qps_min.csv').fillna(0)
data = data.iloc[:3000, :]  # 取前 3000 行
time_len = data.shape[0]

# 选择第 190 个函数的调用数据
print(data)
ts_long = data.iloc[:, [i+2 for i in list(short_col_id)]].sum(axis=1).to_frame("long_sum")
ts = ts_long
print(ts)
ts.index = pd.date_range('2012-03-01', periods=time_len, freq='1min')  # 设置时间索引

# 划分训练集和测试集
train_size = int(time_len * 0.8)
train_ts, test_ts = ts[:train_size], ts[train_size:]

# 训练 ARIMA 模型（记录耗时）
start_train = time.time()
auto_model = pm.auto_arima(train_ts, seasonal=False, stepwise=True, trace=True)
train_time = time.time() - start_train  # 计算训练耗时

# 获取最佳阶数
p, d, q = auto_model.order
# p, d, q = 5, 2, 3
print(f"最佳 ARIMA 阶数: p={p}, d={d}, q={q}")

# 重新拟合 ARIMA 模型
model = ARIMA(train_ts, order=(p, d, q))
proper_model = model.fit()

predict = []
# 进行预测（记录耗时）
start_pred = time.time()
new_model = proper_model.append(test_ts, refit=False)
predict = new_model.predict(start=test_ts.index[0], end=test_ts.index[-1], dynamic=False)
pred_time = time.time() - start_pred  # 计算预测耗时

# # === 计算误差 ===
mse = mean_squared_error(test_ts, predict)
rmse = np.sqrt(mse)
mae = mean_absolute_error(test_ts, predict)
r2 = r2_score(test_ts, predict)

# 计算 MAPE（避免 0 除错误）
def mean_absolute_percentage_error(y_true, y_pred): 
    # 将输入转换为一维数组
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    nonzero_idx = y_true != 0  # 避免除以 0
    return np.mean(np.abs((y_true[nonzero_idx] - y_pred[nonzero_idx]) / y_true[nonzero_idx])) * 100

mape = mean_absolute_percentage_error(test_ts, predict)

# # 打印评估指标
print(f"ARIMA 预测的评估结果：")
print(f"MSE  (均方误差): {mse:.4f}")
print(f"RMSE (均方根误差): {rmse:.4f}")
print(f"MAE  (平均绝对误差): {mae:.4f}")
# print(f"MAPE (平均绝对百分比误差): {mape:.2f}%")
print(f"R²   (决定系数): {r2:.4f}")
print(f"训练耗时: {train_time:.4f} 秒")
print(f"预测耗时: {pred_time:.6f} 秒")
print(f"MAPE (平均绝对百分比误差): {mape:.4f}")

# === 画图 ===
plt.figure(figsize=(15, 4))
plt.plot(test_ts, label="Ground Truth")
plt.plot(predict, label="ARIMA 预测", color="red")
plt.legend()
plt.savefig("arima_qps_prediction.pdf", format="pdf", dpi=300, bbox_inches="tight")
plt.show()
