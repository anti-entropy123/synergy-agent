import uuid
from time import time
import cv2
import sys

from minio import Minio
minioClient=Minio('192.168.1.109:31786',access_key='admin123',secret_key='admin123',secure=False)


tmp = "/tmp/"
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2


def video_processing(object_key, video_path):
    file_name = object_key.split(".")[FILE_NAME_INDEX]
    result_file_path = tmp+file_name+'-output.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    start = time()
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tmp_file_path = tmp+'tmp.jpg'
            cv2.imwrite(tmp_file_path, gray_frame)
            gray_frame = cv2.imread(tmp_file_path)
            out.write(gray_frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()
    return latency, result_file_path


def lambda_handler(event, context):
    input_bucket = event['input_bucket']
    object_key = event['object_key']
    output_bucket = event['output_bucket']

    download_path = tmp+'{}{}'.format(uuid.uuid4(), object_key)

    download_file(input_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    return latency


def execute(width, height, size):
    startTime = time()
    input_bucket = "functionbench"
    object_key = "SampleVideo_"+str(width)+"x"+str(height)+"_"+str(size)+"mb.mp4"

    download_path = tmp+'{}{}'.format(uuid.uuid4(), object_key)

    download_file(input_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    print((time()-startTime)*1000)
    return latency

def download_file(input_bucket, object_key, filepath):
    minioClient.fget_object(input_bucket, object_name=object_key, file_path=filepath)

if __name__ == '__main__':
    execute(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))

