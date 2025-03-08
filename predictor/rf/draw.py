import matplotlib.pyplot as plt
import json

from qps_data_loader.loader import calc_error_rate

# 可视化结果
plt.figure(figsize=(6, 3))
plt.title("rf")

with open("./results/rf_pw_zq_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="pw_zq_actual", linewidth=0.3, linestyle='--', zorder=10)

with open("./results/rf_pw_zq_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="pw_zq_predict", linewidth=0.3)

calc_error_rate("rf_pw_zq", y_test_actual, predictions)

with open("./results/rf_zq_tf_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="zq_tf_actual", linestyle='--', zorder=10, linewidth=0.3)

with open("./results/rf_zq_tf_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="zq_tf_predict", linewidth=0.3)

calc_error_rate("rf_zq_tf", y_test_actual, predictions)


with open("./results/rf_tf_zq_y_test_actual.json", "r") as f:
    y_test_actual = json.loads(f.read())
    plt.plot(y_test_actual, label="tf_zq_actual", linestyle='--', zorder=10, linewidth=0.3)

with open("./results/rf_tf_zq_predictions.json", "r") as f:
    predictions = json.loads(f.read())
    plt.plot(predictions, label="tf_zq_predict", linewidth=0.3)

calc_error_rate("rf_tf_zq", y_test_actual, predictions)


plt.legend()
plt.savefig("./rf/rf_output.pdf")
