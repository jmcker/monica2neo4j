import json
import os

import monica_client

from .driver import Neo4jConnection
from .generate import generate_contacts

if __name__ == "__main__":
    import argparse

    neo4j_url = os.environ.get(
        "NEO4J_URL", "bolt+s://YOUR-OWN-ID.neo4jsandbox.com:7687"
    )
    monica_url = os.environ.get("MONICA_URL", monica_client.DEFAULT_URL)

    parser = argparse.ArgumentParser(
        "monica2neo4j",
        description="Copy contact details and relationships from Monica to a Neo4j graph database",
    )
    parser.add_argument(
        "--monica",
        "-m",
        dest="monica_url",
        action="store",
        default=monica_url,
        help="HTTP(S) address of the desired Monica instance",
    )
    parser.add_argument(
        "--neo4j",
        "-n",
        dest="neo4j_url",
        action="store",
        default=neo4j_url,
        help="Bolt address for the desired Neo4j instance",
    )
    parser.add_argument(
        "--print",
        "-p",
        dest="print",
        action="store_true",
        help="Print the Neo4j queries instead of running them",
    )
    parser.add_argument(
        "--wipe",
        "-w",
        dest="wipe",
        action="store_true",
        help="Clear the ENTIRE database before populating it from Monica. ALL nodes and relationships will be removed",
    )
    parser.add_argument(
        "--force",
        "-f",
        dest="force",
        action="store_true",
        help="Do not prompt for confirmation of prune or wipe",
    )

    args = parser.parse_args()

    try:
        monica_url = args.monica_url
        monica_token = os.environ.get("MONICA_TOKEN", None)
        neo4j_url = args.neo4j_url
        neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
        neo4j_password = os.environ.get("NEO4J_PASSWORD", None)

        if not all([monica_token, neo4j_user, neo4j_password]):
            with open("secrets.json", "r") as f:
                secrets = json.load(f)

            if monica_token is None:
                monica_token = secrets["MONICA_TOKEN"]
            if neo4j_password is None:
                neo4j_password = secrets["NEO4J_PASSWORD"]

        client = monica_client.MonicaApiClient(monica_token, base_url=monica_url)
        db = Neo4jConnection(neo4j_url, neo4j_user, neo4j_password)

        client.test()
        db.test()

        if args.wipe:
            db.reset(force=args.force)

        if args.print:
            contacts_iter = client.contacts(use_iter=True)
            queries = generate_contacts(contacts_iter)

            for query in queries:
                print(query)

        else:
            contacts_iter = client.contacts(use_iter=True)
            db.ingest_contacts(contacts_iter)

    except Exception as e:
        print(repr(e))
