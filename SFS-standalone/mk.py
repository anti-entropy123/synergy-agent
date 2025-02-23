import json
import markdown
import base64
import os
import sys
def f(n):
    try:
        with open('/openpiton-readme.json') as f:
            data = json.load(f)
    except:
        return {'Error' : 'Possibly lacking markdown parameter in request.'}
    text = data["markdown"]
    decoded_text = base64.b64decode(text.encode()).decode()
    return decoded_text

def main():
    n = sys.argv[1]
    f(n)

main()