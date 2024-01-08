import json
import os
import pprint

from . import DEFAULT_URL, MonicaApiClient

if __name__ == "__main__":
    import argparse

    monica_url = os.environ.get("MONICA_URL", DEFAULT_URL)

    parser = argparse.ArgumentParser(
        "monica_client", description="API client for Monica"
    )
    parser.add_argument(
        "--monica",
        "-m",
        dest="monica_url",
        action="store",
        default=monica_url,
        help="HTTP(S) address of the desired Monica instance",
    )

    args = parser.parse_args()

    monica_url = args.monica_url
    monica_token = os.environ.get("MONICA_TOKEN", None)

    if not all([monica_token]):
        with open("secrets.json", "r") as f:
            secrets = json.load(f)

        if monica_token is None:
            monica_token = secrets["MONICA_TOKEN"]

    client = MonicaApiClient(monica_token, monica_url)
    pprint.pprint(client.me())
