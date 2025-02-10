# -*- coding: utf-8 -*-
import subprocess
import re

# 用于存储每次执行的最后一行结果
results = []

# 正则表达式模式，用于匹配 "fib\d+ \d+" 形式的行
pattern = re.compile(r'fib\d+ \d+')

# 执行命令 10 次
for _ in range(10):
    # 执行命令并捕获输出
    result = subprocess.run(['./main', '-p', 'c', '-t', 'test3', '-n', '1'], stdout=subprocess.PIPE, text=True)
    
    # 获取输出并按行分割
    output_lines = result.stdout.strip().split('\n')
    
    # 使用正则表达式匹配 "fib\d+ \d+" 形式的行
    for i in range(len(output_lines)):
        if pattern.match(output_lines[i]):
            # 检查下一行是否为空行或文件末尾
            if i + 1 >= len(output_lines) or output_lines[i + 1].strip() == '':
                results.append(output_lines[i].strip())
                break

# 打印每次执行的最后一行结果
for result in results:
    print(result)