import json
import time
import uuid
import os
import sys
from minio import Minio
import exifread

bucket_name = "serverlessbench"

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    event = json.loads(req)

    currentTime = GetTime()

    print("ExtractImageMetadata invoked")

    #minio_url = event["minio_url"]
    #access_key = event["access_key"]
    #secret_key = event["secret_key"]
    #bucket_name = event["bucket_name"]
    img_name = event["img_name"]

    startTimes = [currentTime]
    
    db_begin = GetTime()
    minioClient=Minio('192.168.1.109:31786',access_key='admin123',secret_key='admin123',secure=False)
    filepath = '/tmp/{}-{}'.format(uuid.uuid4(), img_name)
    minioClient.fget_object(bucket_name, object_name=img_name, file_path=filepath)
    db_finish = GetTime()
    db_elapse_ms = db_finish - db_begin

    commTimes = [db_elapse_ms]

    info = get_exif(filepath)

    os.remove(filepath)    
    return json.dumps({
        "startTimes": startTimes,
        "commTimes": commTimes,
        "extracted-metadata": info,
        "minio_url": event["minio_url"],
        "access_key": event["access_key"],
        "secret_key": event["secret_key"],
        "bucket_name": event["bucket_name"],
        "img_name": img_name
    })


def execute(img_name):
    """handle a request to the function
    Args:
        req (str): request body
    """
    currentTime = GetTime()

    #print("ExtractImageMetadata invoked")

    # minio_url = event["minio_url"]
    # access_key = event["access_key"]
    # secret_key = event["secret_key"]
    # bucket_name = event["bucket_name"]

    startTimes = [currentTime]

    db_begin = GetTime()
    minioClient = Minio('192.168.1.109:31786', access_key='admin123', secret_key='admin123', secure=False)
    filepath = '/tmp/{}-{}'.format(uuid.uuid4(), img_name)
    minioClient.fget_object(bucket_name, object_name=img_name, file_path=filepath)
    db_finish = GetTime()
    db_elapse_ms = db_finish - db_begin

    commTimes = [db_elapse_ms]

    info = get_exif(filepath)

    os.remove(filepath)
    print(GetTime()-currentTime)
    return json.dumps({
        "startTimes": startTimes,
        "commTimes": commTimes,
        "extracted-metadata": info,
        "minio_url": ["minio_url"],
        "access_key": ["access_key"],
        "secret_key": ["secret_key"],
        "bucket_name": ["bucket_name"],
        "img_name": img_name
    })


def get_exif(file_path):
    f = open(file_path, 'rb')
    tag1 = exifread.process_file(f, strict=True)
    tag = {}
    for key, value in tag1.items():
            if key not in ('JPEGThumbnail','TIFFThumbnail','Filename','EXIF MakerNote'):
                tag[key] = str(value)
                #print("%s, %s" % (key, value))
    tag["Filesize"] = str(round(os.stat(file_path).st_size / (1000*1000),3))+"MB"
    tag["Mime type"] = "image/" + file_path.split(".")[-1].strip()
    #tags = json.dumps(tag) 
    return tag    

def GetTime():
    return int(round(time.time() * 1000))


if __name__ == '__main__':
    execute(sys.argv[1])
