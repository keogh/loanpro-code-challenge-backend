from django.conf import settings
import requests


def get_random_string(length, characters):
    url = 'https://api.random.org/json-rpc/4/invoke'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "generateStrings",
        "params": {
            "apiKey": settings.RANDOM_ORG_API_KEY,
            "n": 1,  # number of strings to generate
            "length": length,
            "characters": characters,
            "replacement": True  # allow characters to repeat
        },
        "id": 42
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if response.status_code == 200 and 'result' in result and 'random' in result['result'] and 'data' in result['result']['random']:
        return result['result']['random']['data'][0]
    else:
        return None
