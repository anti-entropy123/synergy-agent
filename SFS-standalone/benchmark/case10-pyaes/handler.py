from time import time
import random
import string
import pyaes
import sys


def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def lambda_handler(event, context):
    length_of_message = event['length_of_message']
    num_of_iterations = event['num_of_iterations']

    message = generate(length_of_message)

    # 128-bit key (16 bytes)
    KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'

    start = time()
    for loops in range(num_of_iterations):
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(message)
        print(ciphertext)

        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)
        print(plaintext)
        aes = None

    latency = time() - start
    return latency


def execute(length_of_message, num_of_iterations):

    startTime = time()
    message = generate(length_of_message)

    # 128-bit key (16 bytes)
    KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'


    for loops in range(num_of_iterations):
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(message)
        #print(ciphertext)

        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)
        #print(plaintext)
        aes = None

    latency = time() - startTime
    print(latency*1000)
    return latency

if __name__ == '__main__':
    execute(int(sys.argv[1]),int(sys.argv[2]))
    #execute(1000000)
    # execute(1000,100)

