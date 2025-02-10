import math
import sys

from time import time


def float_operations(n):
    start = time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    print(latency*1000)
    return latency


def lambda_handler(event, context):
    n = int(event['n'])
    result = float_operations(n)
    return result


def execute(n):
    result = float_operations(n)
    return result

if __name__ == '__main__':
    execute(int(sys.argv[1]))
    #execute(1000000)
