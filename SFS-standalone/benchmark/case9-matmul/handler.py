import numpy as np
import sys
from time import time


def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    return latency


def lambda_handler(event, context):
    n = int(event['n'])
    result = matmul(n)
    print(result)
    return result


def execute(n):
    startTime=time()
    result = matmul(n)
    print((time()-startTime)*1000)
    return result

if __name__ == '__main__':
    execute(int(sys.argv[1]))
    #execute(1000000)
