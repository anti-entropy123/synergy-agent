import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import time

from qps_data_loader.loader import read_data, pw_zq_func_id, zq_tf_func_id, tf_zq_func_id, save_result, calc_error_rate

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 设置随机种子
torch.manual_seed(42)
np.random.seed(42)

# LSTM 模型定义
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=128, num_layers=3):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)  # 预测单个值

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        out = self.fc(lstm_out[:, -1, :])  # 取最后一个时间步的输出
        return out

def train_and_predict(invoc_nums):
    data = np.array(invoc_nums)
    print("data len: ", data.shape)
    # data = np.cumsum(np.random.randn(time_steps) * 10 + 100)  # 模拟调用量数据

    # 数据归一化
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data.reshape(-1, 1))

    # 设定窗口长度（1天 → 预测下一分钟）
    sequence_length = 1440 * 1
    X, y = [], []

    for i in range(len(data_scaled) - sequence_length):
        X.append(data_scaled[i:i+sequence_length])
        y.append(data_scaled[i+sequence_length])

    X, y = np.array(X), np.array(y)

    # 划分训练集（80%）、测试集（20%）
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # 转换为 PyTorch 张量
    X_train = torch.tensor(X_train, dtype=torch.float32)  # (样本数, 时间步, 1)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    X_train, y_train = X_train.to(device), y_train.to(device)
    X_test, y_test = X_test.to(device), y_test.to(device)

    # 模型初始化
    train_start = time.time()
    model = LSTMModel().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.002)

    # 训练 LSTM
    num_epochs = 100
    batch_size = 64
    train_loader = torch.utils.data.DataLoader(list(zip(X_train, y_train)), batch_size=batch_size, shuffle=True)

    for epoch in range(num_epochs):
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.6f}")

    train_time = time.time() - train_start
    pred_start = time.time()
    # 预测
    model.eval()
    with torch.no_grad():
        predictions = model(X_test)

    pred_time = time.time() - pred_start
    
    # 反归一化
    predictions = scaler.inverse_transform(predictions.cpu().numpy())
    y_test_actual = scaler.inverse_transform(y_test.cpu().numpy())
    
    return predictions, y_test_actual, train_time, pred_time


func_to_qps = read_data()

def test_lstm(func_label, func_id):
    print(f"begin lstm_{func_label}")
    predict, actual, t_time, p_time = train_and_predict(func_to_qps[func_id])
    print(t_time, p_time)
    calc_error_rate(f"lstm_{func_label}", predict, actual)
    save_result(f'lstm_{func_label}', predict, actual)

test_lstm("pw_zq", pw_zq_func_id)
test_lstm("zq_tf", zq_tf_func_id)
test_lstm("tf_zq", tf_zq_func_id)