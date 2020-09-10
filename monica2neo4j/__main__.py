import json
from pprint import pprint

from monica_client import MonicaApiClient

from .text import generate_queries

if (__name__ == '__main__'):

    url = 'https://monica.lan.symboxtra.com/api/'

    with open('secrets.json', 'r') as f:
        secrets = json.load(f)

    client = MonicaApiClient(secrets['token'], base_url=url)

    contacts = client.contacts()
    quries = generate_queries(contacts)

    for query in quries:
        print(query)
