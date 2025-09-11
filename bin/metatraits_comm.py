#!/usr/bin/env python3

import argparse
import json

import requests


METATRAITS_URL = "https://metatraits.embl.de/api/v1"



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speci", type=str)
    ap.add_argument("--output", "-o", type=str)
    args = ap.parse_args()

    if args.speci:
        url = f"{METATRAITS_URL}/species_taxonomy/{args.speci}"
        # print(url)
        request = requests.get(url)
        d = request.json()

        # print(d)
        url = f"{METATRAITS_URL}/traits/taxonomy/{d['species_tax_id']}"
        request = requests.get(url, stream=True,)

        # d = request.json()
        with open(args.output, 'wb') as json_out:
            for chunk in request.iter_content(chunk_size=8192):
                json_out.write(chunk)

        # print(json.dumps(request.json(), indent=4))



if __name__ == "__main__":
    main()