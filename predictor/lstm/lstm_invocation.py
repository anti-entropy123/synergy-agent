import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import json

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 设置随机种子
torch.manual_seed(42)
np.random.seed(42)

# 生成模拟时间序列数据（7天的分钟级调用量）
time_steps = 7 * 1440  # 7天，每天1440分钟

pw_zq_func_id = '5315be05fc3b21a3f483ed0759bce825764dcf8a762623a1d94ff63f9d9ce4cc'
zq_tf_func_id = '660323aa6f1012c8eca3c7d8153cb436320b48ed84f82bf3e816b494ad8dfde2'
tf_zq_func_id = 'f8c5d1ba78b7d2f4d2d2a0d8bbc31f0b93185edce1d0788fbc362f22bd931af2'

func_to_qps = {}
func_to_qps[pw_zq_func_id] = []
func_to_qps[zq_tf_func_id] = []
func_to_qps[tf_zq_func_id] = []

def read_data():
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

    # 预测
    model.eval()
    with torch.no_grad():
        predictions = model(X_test)

    # 反归一化
    predictions = scaler.inverse_transform(predictions.cpu().numpy())
    y_test_actual = scaler.inverse_transform(y_test.cpu().numpy())
    
    return predictions, y_test_actual

def save_result(prefix, predictions, y_test_actual):
    with open(f"./{prefix}_y_test_actual.json", "w") as f:
        f.write(json.dumps(y_test_actual.tolist()))

    with open(f"./{prefix}_predictions.json", "w") as f:
        f.write(json.dumps(predictions.tolist()))

read_data()

# print("begin pw_zq")
# func_id = pw_zq_func_id
# predict, actual = train_and_predict(func_to_qps[func_id])
# save_result('pw_zq', predict, actual)

print("begin zq_tf")
func_id = zq_tf_func_id
predict, actual = train_and_predict(func_to_qps[func_id])
save_result('zq_tf', predict, actual)

print("begin tf_zq")
func_id = tf_zq_func_id
predict, actual = train_and_predict(func_to_qps[func_id])
save_result('tf_zq', predict, actual)