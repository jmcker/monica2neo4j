import json
from pprint import pprint

from monica_client import MonicaApiClient

from .driver import Neo4jConnection
from .generate import generate_contacts

if (__name__ == '__main__'):

    neo4j_url = 'bolt://neo4j.lan.symboxtra.com:7687'
    monica_url = 'https://monica.lan.symboxtra.com/api/'

    with open('secrets.json', 'r') as f:
        secrets = json.load(f)

    client = MonicaApiClient(secrets['token'], base_url=monica_url)
    db = Neo4jConnection(neo4j_url, 'neo4j', secrets['neo4j_password'])
    db.reset()

    contacts = client.contacts(use_iter=False)
    # queries = generate_contacts(contacts)

    # for query in queries:
    #     print(query)

    db.ingest_contacts(contacts)
