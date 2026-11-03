#!/usr/bin/env python3

import argparse
import gzip
import os
import pathlib

from collections import Counter

import pandas as pd

from chunk_reader import get_lines_from_chunks


# Supported feature columns from eggNOG-mapper
ALL_FEATURES = {
    'eggNOG_OGs', 'COG_category', 'GOs', 'EC', 'KEGG_ko', 'KEGG_Pathway',
    'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', 'BRITE', 'KEGG_TC',
    'CAZy', 'BiGG_Reaction', 'PFAMs'
}

def load_pfam_mappings(fn):
    # Load PFAM mapping file
    d = {}
    with gzip.open(fn, "rt") as mf:
        for line in mf.readlines():
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                pfam_accession, _, _, pfam_id = parts[:4]
                d[pfam_id] = pfam_accession
    return d

def read_emapper_annotations(fn, features):
    """Read an eggNOG-mapper annotations file, skipping '##' lines."""
    header = None
    for l in get_lines_from_chunks(fn, bufsize=4_000_000):
        if l[:2] != "##":
            l = l.rstrip().split("\t")
            if l[0][0] == "#":
                header = l
            else:
                yield tuple((col, val) for col, val in zip(header, l) if col in features)

def sample_id_from_path(path, emapper_suffix=".emapper.annotations"):
    """Derive a sample identifier from the filename."""
    return os.path.basename(path).replace(".gz", "").replace(emapper_suffix, "")

def main():
    parser = argparse.ArgumentParser(
        description="Generate term-frequency matrices from eggNOG-mapper outputs"
    )
    parser.add_argument(
        '--input-file', nargs='+', required=True,
        help="Paths to one or more eggNOG-mapper .emapper.annotations(.gz) files"
    )
    parser.add_argument(
        '--features', 
        help="Which feature columns to parse; default=all"
    )
    parser.add_argument(
        '--outdir', required=True,
        help="Directory to write output matrices"
    )
    parser.add_argument(
        '--pfam-map-file', default="../data/pfam/Pfam31.0/Pfam-A.clans.tsv.gz",
        help="Path to PFAM-A.clans.tsv.gz mapping file"
    )
    args = parser.parse_args()

    # Load PFAM mapping file
    # global pfam_short_to_accession, pfam_mapped_count, pfam_unmapped_count
    pfam_map = load_pfam_mappings(args.pfam_map_file)
    pfam_mapped_count = 0
    pfam_unmapped_count = 0

    features = set(args.features.split(",")) if args.features else ALL_FEATURES
    # counts[feature][sample] = { term: count, ... }
    counts = {feat: {} for feat in features}

    pathlib.Path(args.outdir).mkdir(exist_ok=True, parents=True,)

    for path in args.input_file:
        sample = sample_id_from_path(path)
        print(f"Processing sample: {sample}")

        for annotation in read_emapper_annotations(path, features):
            for feature, value in annotation:
                terms = tuple(t for t in value.split(",") if t and t != "-")
                if not terms:
                    continue
                if feature == "PFAMs":
                    terms = tuple((t, pfam_map.get(t)) for t in terms)
                    _, mapped_terms = zip(*terms)
                    unmapped = mapped_terms.count(None)
                    pfam_unmapped_count += unmapped
                    pfam_mapped_count += len(terms) - unmapped
                    terms = ((t[0] if t[1] is None else t[1]) for t in terms)
                counts[feature].setdefault(sample, Counter()).update(terms)

        # For each feature, write term-frequency matrix
    for feat in features:
        feat_counts = counts.get(feat, {})
        if not feat_counts:
            print(f"Skipping '{feat}': no data")
            continue

        # all unique terms
        all_terms = sorted({t for sample_counts in feat_counts.values() for t in sample_counts})
        # build DataFrame: rows=samples, cols=terms
        mat = pd.DataFrame(
            0,
            index=sorted(feat_counts.keys()),
            columns=all_terms,
            dtype=int
        )
        for sample, sample_counts in feat_counts.items():
            for term, c in sample_counts.items():
                mat.at[sample, term] = c

        # save counts matrix
        out_counts = os.path.join(args.outdir, f"{sample}.emapper.{feat}.tsv.gz")
        mat.to_csv(out_counts, sep='\t', compression='gzip', index_label='sample')
        print(f"Wrote counts matrix: {out_counts}")

    if 'PFAMs' in features:
        total = pfam_mapped_count + pfam_unmapped_count
        pct = pfam_mapped_count / total * 100 if total > 0 else 0
        print(f"PFAM mapping summary: {pfam_mapped_count}/{total} mapped ({pct:.1f}%).")


if __name__ == '__main__':
    main()