
from time import time
from PIL import Image, ImageFilter
import sys
import uuid

from minio import Minio


minioClient=Minio('192.168.1.109:31786',access_key='admin123',secret_key='admin123',secure=False)

FILE_NAME_INDEX = 2
default_bucket = "functionbench"

def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += flip(image, file_name)
        path_list += rotate(image, file_name)
        path_list += filter(image, file_name)
        path_list += gray_scale(image, file_name)
        path_list += resize(image, file_name)

    latency = time() - start
    return latency, path_list


def lambda_handler(event, context):
    startTime = time()
    input_bucket = event['input_bucket']
    object_key = event['object_key']

    file_path = '/tmp/{}{}'.format(uuid.uuid4(), object_key)
    download_file(input_bucket, object_key, file_path)
    latency, path_list = image_processing(object_key, file_path)
    print((time()-startTime)*1000)
    return latency

def execute(file_name):
    startTime = time()
    file_path = "/tmp/{}-{}".format(uuid.uuid4(), file_name)
    download_file(default_bucket, file_name, file_path)

    latency, path_list = image_processing(file_name, file_path)
    print((time() - startTime) * 1000)
    return latency


def download_file(input_bucket, object_key, filepath):
    minioClient.fget_object(input_bucket, object_name=object_key, file_path=filepath)



TMP = "/tmp/"


def flip(image, file_name):
    path_list = []
    path = TMP + "flip-left-right-" + file_name
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(path)
    path_list.append(path)

    path = TMP + "flip-top-bottom-" + file_name
    img = image.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    path_list.append(path)

    return path_list


def rotate(image, file_name):
    path_list = []
    path = TMP + "rotate-90-" + file_name
    img = image.transpose(Image.ROTATE_90)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-180-" + file_name
    img = image.transpose(Image.ROTATE_180)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-270-" + file_name
    img = image.transpose(Image.ROTATE_270)
    img.save(path)
    path_list.append(path)

    return path_list


def filter(image, file_name):
    path_list = []
    path = TMP + "blur-" + file_name
    img = image.filter(ImageFilter.BLUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "contour-" + file_name
    img = image.filter(ImageFilter.CONTOUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "sharpen-" + file_name
    img = image.filter(ImageFilter.SHARPEN)
    img.save(path)
    path_list.append(path)

    return path_list


def gray_scale(image, file_name):
    path = TMP + "gray-scale-" + file_name
    img = image.convert('L')
    img.save(path)
    return [path]


def resize(image, file_name):
    path = TMP + "resized-" + file_name
    image.thumbnail((128, 128))
    image.save(path)
    return [path]


if __name__ == '__main__':
    execute(sys.argv[1])
