import matplotlib.pyplot as plt
import json


# 可视化结果
plt.figure(figsize=(10, 5))

with open("./results/pw_zq_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="pw_zq_actual", linestyle='--', zorder=10)

with open("./results/pw_zq_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="pw_zq_predict")

with open("./results/tf_zq_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="tf_zq_actual", linestyle='--', zorder=10)

with open("./results/tf_zq_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="tf_zq_predict")

with open("./results/zq_tf_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="zq_tf_actual", linestyle='--', zorder=10)

with open("./results/zq_tf_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="zq_tf_predict")

plt.legend()
plt.savefig("./lstm/lstm_output.pdf")
