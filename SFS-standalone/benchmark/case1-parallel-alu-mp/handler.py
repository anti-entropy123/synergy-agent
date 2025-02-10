import random
import time
import multiprocessing as mp 
import sys

def handle(req):
    startTime = GetTime()
    event = eval(req)
    if 'parallelIndex' in event:
        looptime = event['looptime']
        parallelIndex = event['parallelIndex']
        temp = execute(looptime, parallelIndex)
        tot_exec = 0
        tempdict = eval(temp)
        for execTime in tempdict:
            tot_exec += int(execTime)
        avg_exec = tot_exec / parallelIndex
        return{
            'result': temp,
            'avg_exec': avg_exec,
            'looptime': looptime,
            'execTime': GetTime() - startTime
        }
    else:
        return{
            'error': "No n in event"
        }
    

def GetTime():
    return int(round(time.time() * 1000))

def execute(looptime, parallelIndex):
    startTime = GetTime()

    payload = int(looptime / parallelIndex)
    resultTexts = []
    processes = []
    p_conns = []
    for i in range(parallelIndex):
        parent_conn, child_conn = mp.Pipe()
        p_conns.append(parent_conn)
        p = mp.Process(target=alu_single, args=(payload, child_conn))
        processes.append(p)
        resultTexts.append('')
    for i in range(parallelIndex):
        processes[i].start()
    for i in range(parallelIndex):
        processes[i].join()
    for i in range(parallelIndex):
        resultTexts[i] = p_conns[i].recv()

    print(GetTime() - startTime)
    return str(resultTexts)

def alu_single(payload, conn):
    result = alu_handler(payload)
    conn.send(str(result['execTime']))
    conn.close()
    return result


def alu_handler(looptime):
    startTime = GetTime()
    temp = alu(looptime)
    #print(GetTime() - startTime)
    return {
        'result': temp,
        'times': looptime,
        'execTime': GetTime() - startTime
    }


def alu(looptime):
    a = random.randint(10, 100)
    b = random.randint(10, 100)
    temp = 0
    for i in range(looptime):
        if i % 4 == 0:
            temp = a + b
        elif i % 4 == 1:
            temp = a - b
        elif i % 4 == 2:
            temp = a * b
        else:
            temp = a / b
    #print(times)
    return temp

if __name__ == '__main__':
    # execute(looptime, parallelIndex)
    execute(int(sys.argv[1]),int(sys.argv[2]))
    # execute(1000000,4)
