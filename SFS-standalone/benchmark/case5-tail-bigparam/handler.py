import json
import time
import hashlib
import sys
from minio import Minio


bucketName = "serverlessbench"

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    event = json.loads(req)

    startTime = GetTime()
    payload_size = event['payload_size']
    text = download_file(payload_size)
    downloadTime = GetTime()
    print(text)

    retTime = event['retTime']
    uploadTime = event['uploadTime']
    print("startTime:" + str(startTime))
    print("downloadTime:" + str(downloadTime))
    wholeCommTime = downloadTime - uploadTime
    commTime = startTime - retTime

    # upload_file(payload_size)
    return json.dumps({
        'wholeCommTime': wholeCommTime,
        'commTime': commTime
    })


def execute(payload_size):
    """handle a request to the function
    Args:
        req (str): request body
    """
    payload_size=int(payload_size)
    startTime = GetTime()
    text = download_file(payload_size)
    #print(text)
    md5(text)

    print(GetTime()-startTime)
    # upload_file(payload_size)
    return json.dumps({
        'wholeCommTime': 0,
        'commTime': 0
    })

def download_file(payload_size):
    path = "payload_%d.json" %payload_size
    filepath = "/tmp/%s" %path
    minioClient = Minio('192.168.1.109:31786', access_key = 'admin123', secret_key = 'admin123', secure = False)
    minioClient.fget_object(bucketName, object_name=path, file_path=filepath)
    with open(filepath, 'r') as f:
        #f.seek(0)
        text = f.read()
        return text

def md5(text):
    hl = hashlib.md5()
    hl.update(text.encode('utf-8'))
    #print(text)
    sign = hl.hexdigest()
    #print(sign)
    password = "gxbdb684f1b8cfdf046744ea96d9fce48469fbac305dc6aa0d6operator_pro1520391961274j4102412y5210ying"
    if text == password:
        return 1
    else:
        return 0

    #import hashlib
    #md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    #print(md5)

def GetTime():
    return int(round(time.time() * 1000))   


if __name__ == '__main__':
    execute(sys.argv[1])
    #execute(1)
