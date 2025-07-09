#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def predict(pfam_fp, model_dir, outdir, k):
    """
    Returns:
        successful: list of phenotype names processed
        binary_calls: dict mapping phenotype -> binary call Series
    """
    # 1) Read PFAM matrix
    comp = 'gzip' if pfam_fp.endswith('.gz') else None
    pf_df = pd.read_csv(pfam_fp, sep='\t', index_col=0, compression=comp)
    X_full = (pf_df > 0).astype(int)

    # 2) Load phenotype list from pt2acc.txt
    pt2acc_path = os.path.join(model_dir, "pt2acc.txt")
    pt2acc = pd.read_csv(pt2acc_path, sep='\t', index_col=0, encoding='utf-8')
    # ensure phenotype codes are strings so we can look up descriptions
    pt2acc.index = pt2acc.index.astype(str)
    traits = pt2acc.index.astype(str).tolist()

    # get description column name (first column in pt2acc)
    desc_col = pt2acc.columns[0]

    os.makedirs(outdir, exist_ok=True)
    successful = []
    binary_calls = {}

    # 3) For each phenotype, extract bias and predictors, compute scores
    for pt in traits:
        print(f"Starting prediction for phenotype '{pt}'")
        try:
            # load bias
            bias_path = os.path.join(model_dir, f"{pt}_bias.txt")
            bias = pd.read_csv(bias_path, sep='\t', index_col=0, header=None)
            # load predictors
            pred_path = os.path.join(model_dir, f"{pt}_feats.txt")
            predictors = pd.read_csv(pred_path, sep='\t', index_col=0)
        except FileNotFoundError:
            print(f"  No model files for '{pt}', skipping.")
            continue

        # Align PFAM matrix to predictor features, filling missing with 0
        data_n = X_full.reindex(columns=predictors.index, fill_value=0).astype(int)
        # compute k raw scores
        preds = np.zeros((X_full.shape[0], k))
        for i in range(k):
            preds[:, i] = bias.iloc[i, 0] + predictors.iloc[:, i].dot(data_n.T)
        raw_df = pd.DataFrame(preds, index=pf_df.index)

        # compute binary calls via majority vote on raw scores
        votes = (raw_df > 0).sum(axis=1)
        threshold = k // 2 + 1
        binary_calls[pt] = (votes >= threshold).astype(int)

        # convert to probabilities and mean
        prob_df = sigmoid(raw_df)
        mean_p = prob_df.mean(axis=1)

        # get human-readable phenotype name
        desc = pt2acc.at[pt, desc_col]

        # write per-trait probability
        out_prob = os.path.join(outdir, f"{pt}.tsv.gz")
        mean_p.to_csv(out_prob, sep='\t', header=[desc], index_label='sample', compression='gzip')
        print(f"  Probability file: {out_prob}")
        successful.append(pt)

    return successful, binary_calls

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Predict Traitar phenotypes from a PFAM matrix"
    )
    parser.add_argument(
        "--pfam-matrix", required=True,
        help="Path to the samples×PFAM annotation matrix (TSV, gzip OK)"
    )
    parser.add_argument(
        "--model-dir", required=True,
        help="Path to the Traitar PhenotypeCollection directory"
    )
    parser.add_argument(
        "--outdir", required=True,
        help="Directory to write per-trait and merged predictions"
    )
    parser.add_argument(
        "-k", "--voters", type=int, default=5,
        help="Number of SVM models to use per phenotype"
    )
    args = parser.parse_args()

    successful, binary_calls = predict(
        args.pfam_matrix,
        args.model_dir,
        args.outdir,
        args.voters
    )

    # reload pt2acc to map codes to descriptions
    pt2acc_path = os.path.join(args.model_dir, "pt2acc.txt")
    pt2acc = pd.read_csv(pt2acc_path, sep='\t', index_col=0, encoding='utf-8')
    pt2acc.index = pt2acc.index.astype(str)
    desc_col = pt2acc.columns[0]

    # Merge probability tables
    if successful:
        merged = pd.DataFrame(index=pd.read_csv(args.pfam_matrix, sep='\t', index_col=0).index)
        for pt in successful:
            fpath = os.path.join(args.outdir, f"{pt}.tsv.gz")
            df = pd.read_csv(fpath, sep='\t', index_col=0, compression='gzip')
            desc = pt2acc.at[pt, desc_col]
            merged[desc] = df[desc]
        merged_prob_fp = os.path.join(args.outdir, "Traitar.prob.tsv.gz")
        merged.to_csv(merged_prob_fp, sep='\t', compression='gzip', index_label='sample')
        print(f"Merged probability table saved to {merged_prob_fp}")

        # Merge binary calls via original majority vote
        if successful:
            merged_bin = pd.DataFrame(index=pd.read_csv(args.pfam_matrix, sep='\t', index_col=0).index)
            for pt in successful:
                desc = pt2acc.at[pt, desc_col]
                merged_bin[desc] = binary_calls[pt]
            merged_bin_fp = os.path.join(args.outdir, "Traitar.binary.tsv.gz")
            merged_bin.to_csv(merged_bin_fp, sep='\t', compression='gzip', index_label='sample')
            print(f"Merged binary table saved to {merged_bin_fp}")
