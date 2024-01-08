import json
from pprint import pprint

from . import MonicaApiClient

if __name__ == "__main__":
    url = "https://monica.lan.symboxtra.com/api/"

    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    client = MonicaApiClient(secrets["token"], base_url=url)
    pprint(client.me())
