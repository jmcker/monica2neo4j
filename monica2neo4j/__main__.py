import argparse
import json
from pprint import pprint
from urllib.parse import urljoin

from monica_client import MonicaApiClient

from .driver import Neo4jConnection
from .generate import generate_contacts

if (__name__ == '__main__'):

    neo4j_url = 'bolt://neo4j.lan.symboxtra.com:7687'
    monica_base_url = 'https://monica.lan.symboxtra.com'

    parser = argparse.ArgumentParser('monica2neo4j', description='Copy contact details and relationships from Monica to a Neo4j graph database')
    parser.add_argument('--monica', '-m', dest='monica_base_url', action='store', default=monica_base_url, help='HTTP(S) address of the desired Monica instance')
    parser.add_argument('--neo4j', '-n', dest='neo4j_url', action='store', default=neo4j_url, help='Bolt address for the desired Neo4j instance')
    parser.add_argument('--print', '-p', dest='print', action='store_true', help='Print the Neo4j queries instead of running them')
    parser.add_argument('--wipe', '-w', dest='wipe', action='store_true', help='Clear the ENTIRE database before populating it from Monica. ALL nodes and relationships will be removed')
    parser.add_argument('--force', '-f', dest='force', action='store_true', help='Do not prompt for confirmation of prune or wipe')

    args = parser.parse_args()

    monica_url = urljoin(args.monica_base_url + '/', 'api/')

    try:
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)

        client = MonicaApiClient(secrets['token'], base_url=monica_url)
        db = Neo4jConnection(args.neo4j_url, 'neo4j', secrets['neo4j_password'])

        if (args.wipe):
            db.reset(force=args.force)

        if (args.print):
            contacts_iter = client.contacts(use_iter=True)
            queries = generate_contacts(contacts_iter)

            for query in queries:
                print(query)

        else:
            contacts_iter = client.contacts(use_iter=True)
            db.ingest_contacts(contacts_iter)

    except Exception as e:
        print(repr(e))
