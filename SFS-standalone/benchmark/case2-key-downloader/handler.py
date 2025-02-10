import time
import os
import sys
import json
import uuid

from minio import Minio

minioClient=Minio('192.168.1.109:31786',access_key='admin123',secret_key='admin123',secure=False)

bucketName = "serverlessbench"
defaultKey = "loopTime.txt"


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    event = json.loads(req)
    startTime = GetTime()
    if 'key' in event:
        key = event['key']
    else:
        key = defaultKey

    filepath = "/tmp/{}-{}".format(uuid.uuid4(), "loopTime.txt")
    download_file(key, filepath)
    loopTime = extractLoopTime(filepath)

    retTime = GetTime()
    return json.dumps({
        "startTime": startTime,
        "retTime": retTime,
        "execTime": retTime - startTime,
        "loopTime": loopTime,
        "key": key
    })


def execute(size):
    """handle a request to the function
    Args:
        req (str): request body
    """
    startTime = GetTime()
    fileName = "file_"+str(size)+"k.txt"
    filepath = "/tmp/{}-{}".format(uuid.uuid4(), fileName)
    download_file(fileName, filepath)
    loopTime = extractLoopTime(filepath)

    retTime = GetTime()
    print(retTime - startTime)
    return json.dumps({
        "startTime": startTime,
        "retTime": retTime,
        "execTime": retTime - startTime,
        "loopTime": loopTime,
        "fileName": fileName
    })

def download_file(key, filepath):
    minioClient.fget_object(bucketName, object_name=key, file_path=filepath)

def extractLoopTime(filepath):
    txtfile = open(filepath, 'rb')
    loopTime = int(txtfile.readline())
    txtfile.close()
    os.remove(filepath)
    return loopTime

def GetTime():
    return int(round(time.time() * 1000))

if __name__ == '__main__':
    execute(sys.argv[1])
