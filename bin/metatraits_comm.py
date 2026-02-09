#!/usr/bin/env python3

import argparse
import json
import re

import requests


METATRAITS_URL = "https://metatraits.embl.de"
METATRAITS_API_URL = f"{METATRAITS_URL}/api/v1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speci", type=str)
    ap.add_argument("--lineage", type=str)
    ap.add_argument("--output", "-o", type=str)
    args = ap.parse_args()


    rank, taxname = None, None
    if args.speci:
        url = f"{METATRAITS_API_URL}/species_taxonomy/{args.speci}"
        request = requests.get(url)
        d = request.json()
        taxonomy, rank, taxname = "ncbi", "species", d.get("species_name")
        with open(f"{args.output}.tax.json", "wt") as _out:
            json.dump(d, _out)
        output_fn = f"{args.output}.traits_from_speci.json"
    elif args.lineage:
        lineage = [
            item.split("__") for item in args.lineage.strip().split(";") if item[-2:] != "__"
        ]
        if lineage:
            taxonomy, (rank, taxname) = "gtdb", lineage[-1]
            rank = {"d": "domain", "p": "phylum", "c": "class", "o": "order", "f": "family", "g": "genus", "s": "species",}.get(rank, "species")
        output_fn = f"{args.output}.traits_from_lineage.json"

    if taxname is None:
        raise ValueError(f"Could not infer taxname from input {args}")
    
    
    
    # https://metatraits.embl.de/taxonomy/download?query=Bacteroides+uniformis&rank=species
    url = f"{METATRAITS_URL}/taxonomy/download"
    params = {
        "query": taxname,
        "rank": rank,
        "taxonomy": taxonomy,
    }
    headers = {
        "Content-Disposition": "inline",
    }

    request = requests.get(url, params=params, headers=headers)

    with open(output_fn, 'wb') as json_out:
        if request:
            print(request.url)
            
            for chunk in request.iter_content(chunk_size=8192):
                json_out.write(chunk)


    return None


if __name__ == "__main__":
    main()