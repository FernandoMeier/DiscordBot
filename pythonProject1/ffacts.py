import requests


def get_request(link, name):
    x = requests.get(link)
    content_json = x.json()
    y = content_json.get(name)
    return y
