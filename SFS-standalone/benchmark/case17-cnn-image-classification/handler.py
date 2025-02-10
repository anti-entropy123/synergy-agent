from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import uuid
from time import time
import sys

from squeezenet import SqueezeNet

#from minio import Minio
#

tmp = "/tmp/"
input_bucket = "functionbench"
model_bucket = "functionbench"

def predict(img_local_path):
    start = time()
    model = SqueezeNet(weights='imagenet')
    img = image.load_img(img_local_path, target_size=(227, 227))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    res = decode_predictions(preds)
    latency = time() - start
    return latency, res


def lambda_handler(event, context):
    input_bucket = event['input_bucket']
    object_key = event['object_key']

    model_object_key = event['model_object_key']  # example : squeezenet_weights_tf_dim_ordering_tf_kernels.h5
    model_bucket = event['model_bucket']

    download_path = tmp + '{}{}'.format(uuid.uuid4(), object_key)
    download_file(input_bucket, object_key, download_path)

    model_path = tmp + '{}{}'.format(uuid.uuid4(), model_object_key)
    download_file(model_bucket, model_object_key, model_path)
        
    latency, result = predict(download_path)
        
    _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}

    return latency


def execute(object_key):
    startTime = time()
    model_object_key = "squeezenet_weights_tf_dim_ordering_tf_kernels.h5"

    #download_path = tmp + '{}{}'.format(uuid.uuid4(), object_key)
    #download_file(input_bucket, object_key, download_path)



    model_path = tmp + '{}{}'.format(uuid.uuid4(), model_object_key)
    download_file(model_bucket, model_object_key, model_path)

    model_path = tmp + "/squeezenet_weights_tf_dim_ordering_tf_kernels.h5"
    download_path = tmp + object_key

    latency, result = predict(download_path)

    _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}

    print((time()-startTime)*1000)
    return latency

def download_file(input_bucket, object_key, filepath):
    #minioClient = Minio('192.168.1.109:31786', access_key='admin123', secret_key='admin123', secure=False)
    #minioClient.fget_object(input_bucket, object_name=object_key, file_path=filepath)
    return

if __name__ == '__main__':
    execute(sys.argv[1])


