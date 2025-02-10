import re

# 从文件中读取数据
with open('cpu_usage.txt', 'r') as file:
    data = file.read()

# 使用正则表达式匹配所有的CPU Usage列表
matches = re.findall(r'Overall CPU Usage per core: \[([^\]]+)\]', data)

# 提取每个列表中的第二个值
second_values = []
for match in matches:
    values = [float(value) for value in match.split(', ')]
    if len(values) > 1:  # 确保列表中有足够的值
        second_values.append(values[1])

# 计算所有第二个值的均值
if second_values:
    mean_value = sum(second_values) / len(second_values)
    print(f'所有提取的第二个值: {second_values}')
    print(f'均值: {mean_value}')
else:
    print('未找到任何第二个值')

# import re

# # 从文件中读取数据
# with open('cpu_usage.txt', 'r') as file:
#     data = file.read()

# # 使用正则表达式匹配所有的CPU Usage列表
# matches = re.findall(r'Overall CPU Usage per core: \[([^\]]+)\]', data)

# # 提取每个列表中的第二个值
# second_values = []
# for match in matches:
#     values = [float(value) for value in match.split(', ')]
#     if len(values) > 1:  # 确保列表中有足够的值
#         second_values.append(values[1])

# # 去除所有数据中的最大值和最小值
# if len(second_values) > 2:
#     max_value = max(second_values)
#     min_value = min(second_values)
#     second_values = [value for value in second_values if value != max_value and value != min_value]

# # 计算剩余值的均值
# if second_values:
#     mean_value = sum(second_values) / len(second_values)
#     print(f'去除最大值和最小值后的第二个值: {second_values}')
#     print(f'均值: {mean_value}')
# else:
#     print('未找到足够的第二个值用于计算')