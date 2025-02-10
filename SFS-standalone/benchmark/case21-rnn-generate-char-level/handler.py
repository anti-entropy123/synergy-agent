#import minio
import os
import pickle
import torch
import rnn
import sys

from time import time

tmp = "/tmp/"

"""
Language
 - Italian, German, Portuguese, Chinese, Greek, Polish, French
 - English, Spanish, Arabic, Crech, Russian, Irish, Dutch
 - Scottish, Vietnamese, Korean, Japanese
"""


def lambda_handler(event, context):
    language = event['language']
    start_letters = event['start_letters']

    model_parameter_object_key = event['model_parameter_object_key']  # example : rnn_params.pkl
    model_object_key = event['model_object_key']  # example : rnn_model.pth
    model_bucket = event['model_bucket']

    # Load pre-processing parameters
    # Check if model parameters are available
    parameter_path = tmp + model_parameter_object_key
    if not os.path.isfile(parameter_path):
        download_file(model_bucket, model_parameter_object_key, parameter_path)

    with open(parameter_path, 'rb') as pkl:
        params = pickle.load(pkl)

    all_categories = params['all_categories']
    n_categories = params['n_categories']
    all_letters = params['all_letters']
    n_letters = params['n_letters']

    # Check if models are available
    # Download model from S3 if model is not already present
    model_path = tmp + model_object_key
    if not os.path.isfile(model_path):
        download_file(model_bucket, model_object_key, model_path)

    rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
    rnn_model.load_state_dict(torch.load(model_path))
    rnn_model.eval()

    start = time()
    output_names = list(rnn_model.samples(language, start_letters))
    latency = time() - start

    return {'latency': latency, 'predict': output_names}


def download_file(input_bucket, object_key, filepath):
    #minioClient = Minio('192.168.1.109:31786', access_key='admin123', secret_key='admin123', secure=False)
    #minioClient.fget_object(input_bucket, object_name=object_key, file_path=filepath)
    return

def execute(language, start_letters):

    # Load pre-processing parameters
    # Check if model parameters are available
    parameter_path = tmp + "rnn_params.pkl"
    with open(parameter_path, 'rb') as pkl:
        params = pickle.load(pkl)

    all_categories = params['all_categories']
    n_categories = params['n_categories']
    all_letters = params['all_letters']
    n_letters = params['n_letters']

    # Check if models are available
    # Download model from S3 if model is not already present
    model_path = tmp + "rnn_model.pth"

    rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
    rnn_model.load_state_dict(torch.load(model_path))
    rnn_model.eval()

    start = time()
    output_names = list(rnn_model.samples(language, start_letters))
    latency = time() - start
    print(latency*1000)
    return {'latency': latency, 'predict': output_names}

if __name__ == '__main__':
    execute(sys.argv[1],sys.argv[2])
