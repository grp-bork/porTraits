#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import gzip
import io

# Supported feature columns from eggNOG-mapper
ALL_FEATURES = [
    'eggNOG_OGs', 'COG_category', 'GOs', 'EC', 'KEGG_ko', 'KEGG_Pathway',
    'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', 'BRITE', 'KEGG_TC',
    'CAZy', 'BiGG_Reaction', 'PFAMs'
]

def read_emapper_annotations(path):
    """Read an eggNOG-mapper annotations file, skipping '##' lines."""
    comp = 'gzip' if path.endswith('.gz') else None
    with (gzip.open(path, 'rt') if comp == 'gzip' else open(path, 'r')) as f:
        lines = [l for l in f if not l.startswith('##')]
    df = pd.read_csv(io.StringIO(''.join(lines)), sep='\t')
    return df

def sample_id_from_path(path):
    """Derive a sample identifier from the filename (before first dot)."""
    name = os.path.basename(path)
    return name.split('.')[0]

def build_feature_counts(df, feature):
    """Split comma-separated terms in df[feature] and count occurrences."""
    global pfam_mapped_count, pfam_unmapped_count
    series = df.get(feature)
    if series is None:
        return {}
    counts = {}
    for entry in series.dropna().astype(str):
        for term in entry.split(','):
            if not term or term == '-':
                continue
            if feature == 'PFAMs':
                mapping = pfam_short_to_accession.get(term)
                if mapping:
                    pfam_mapped_count += 1
                    term = mapping
                else:
                    pfam_unmapped_count += 1
                    # term remains unchanged
            counts[term] = counts.get(term, 0) + 1
    return counts

def main():
    parser = argparse.ArgumentParser(
        description="Generate term-frequency matrices from eggNOG-mapper outputs"
    )
    parser.add_argument(
        '--input-file', nargs='+', required=True,
        help="Paths to one or more eggNOG-mapper .emapper.annotations(.gz) files"
    )
    parser.add_argument(
        '--features', nargs='+', choices=ALL_FEATURES,
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
    mapping_file = args.pfam_map_file
    global pfam_short_to_accession, pfam_mapped_count, pfam_unmapped_count
    pfam_short_to_accession = {}
    pfam_mapped_count = 0
    pfam_unmapped_count = 0
    with gzip.open(mapping_file, "rt") as mf:
        for line in mf:
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                pfam_accession, _, _, pfam_id = parts[:4]
                pfam_short_to_accession[pfam_id] = pfam_accession

    features = args.features if args.features else ALL_FEATURES
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # counts[feature][sample] = { term: count, ... }
    counts = {feat: {} for feat in features}

    for path in args.input_file:
        sample = sample_id_from_path(path)
        print(f"Processing sample: {sample}")
        df = read_emapper_annotations(path)
        for feat in features:
            if feat not in df.columns:
                print(f"  Warning: feature '{feat}' not in {path}; skipping")
                continue
            cnts = build_feature_counts(df, feat)
            counts[feat][sample] = cnts

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
        out_counts = os.path.join(outdir, f"emapper.{feat}.tsv.gz")
        mat.to_csv(out_counts, sep='\t', compression='gzip', index_label='sample')
        print(f"Wrote counts matrix: {out_counts}")

    if 'PFAMs' in features:
        total = pfam_mapped_count + pfam_unmapped_count
        pct = pfam_mapped_count / total * 100 if total > 0 else 0
        print(f"PFAM mapping summary: {pfam_mapped_count}/{total} mapped ({pct:.1f}%).")

if __name__ == '__main__':
    main()