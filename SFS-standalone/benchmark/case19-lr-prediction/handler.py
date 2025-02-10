#import minio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import pandas as pd
from time import time
import sys
import os
import re

tmp = '/tmp/'
cleanup_re = re.compile('[^a-z]+')


def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence


def lambda_handler(event, context):
    x = event['x']

    dataset_object_key = event['dataset_object_key']
    dataset_bucket = event['dataset_bucket']

    model_object_key = event['model_object_key']  # example : lr_model.pk
    model_bucket = event['model_bucket']

    model_path = tmp + model_object_key
    if not os.path.isfile(model_path):
        download_file(model_bucket, model_object_key, model_path)

    dataset_path = 's3://'+dataset_bucket+'/'+dataset_object_key
    dataset = pd.read_csv(dataset_path)

    start = time()

    df_input = pd.DataFrame()
    df_input['x'] = [x]
    df_input['x'] = df_input['x'].apply(cleanup)

    dataset['train'] = dataset['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])

    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load(model_path)
    y = model.predict(X)

    latency = time() - start

    return {'y': y, 'latency': latency}



def execute(data_size):
    x = "I have bought several of the Vitality canned dog food products and have found them all to be of good quality. The product looks more like a stew than a processed meat and it smells better. My Labrador is finicky and she appreciates this product better than  most."

    model_path = tmp + "lr_model.pk"

    dataset_path = tmp + "reviews" + data_size + "mb.csv"
    dataset = pd.read_csv(dataset_path)

    start = time()

    df_input = pd.DataFrame()
    df_input['x'] = [x]
    df_input['x'] = df_input['x'].apply(cleanup)

    dataset['train'] = dataset['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])

    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load(model_path)
    y = model.predict(X)

    latency = time() - start

    print(latency*1000)
    return {'y': y, 'latency': latency}

def download_file(input_bucket, object_key, filepath):
    #minioClient = Minio('192.168.1.109:31786', access_key='admin123', secret_key='admin123', secure=False)
    #minioClient.fget_object(input_bucket, object_name=object_key, file_path=filepath)
    return

if __name__ == '__main__':
    execute(sys.argv[1])

