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
        prob_calls: dict mapping phenotype -> mean probability Series
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

    # create mapping from phenotype ID to description
    trait_names = {
        pt: pt2acc.at[pt, desc_col]
        for pt in traits if pt in pt2acc.index
    }

    os.makedirs(outdir, exist_ok=True)
    successful = []
    binary_calls = {}
    prob_calls = {}

    # 3) For each phenotype, extract bias and predictors, compute scores
    for pt in traits:
        print(f"Starting prediction for phenotype '{trait_names.get(pt, pt)}'")
        try:
            # load bias
            bias_path = os.path.join(model_dir, f"{pt}_bias.txt")
            bias = pd.read_csv(bias_path, sep='\t', index_col=0, header=None)
            # load predictors
            pred_path = os.path.join(model_dir, f"{pt}_feats.txt")
            predictors = pd.read_csv(pred_path, sep='\t', index_col=0)
        except FileNotFoundError:
            print(f"  No model files for '{trait_names.get(pt, pt)}', skipping.")
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

        # collect mean probabilities
        prob_calls[pt] = mean_p

        print(f"  Completed prediction for phenotype '{trait_names.get(pt, pt)}'")
        successful.append(pt)

    binary_calls_named = {trait_names.get(pt, pt): series for pt, series in binary_calls.items()}
    prob_calls_named = {trait_names.get(pt, pt): series for pt, series in prob_calls.items()}

    return successful, binary_calls_named, prob_calls_named

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
        help="Path to the Traitar PhenotypeCollection directory that holds model subdirectories."
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

    model_dirs = [
        d for d in os.listdir(args.model_dir)
        if os.path.isdir(os.path.join(args.model_dir, d))
    ]

    all_binary_calls = {}
    all_successful = {}
    pt2acc_dict = {}
    all_prob_calls = {}

    for model_name in model_dirs:
        model_path = os.path.join(args.model_dir, model_name)
        output_path = args.outdir

        successful, binary_calls, prob_calls = predict(
            args.pfam_matrix,
            model_path,
            output_path,
            args.voters
        )
        all_binary_calls[model_name] = binary_calls
        all_successful[model_name] = successful
        all_prob_calls[model_name] = prob_calls

        pt2acc_path = os.path.join(model_path, "pt2acc.txt")
        pt2acc = pd.read_csv(pt2acc_path, sep='\t', index_col=0, encoding='utf-8')
        pt2acc.index = pt2acc.index.astype(str)
        pt2acc_dict[model_name] = pt2acc

    for model_name, binary_dict in all_binary_calls.items():
        wide_bin = pd.DataFrame(binary_dict)
        desc_col = pt2acc_dict[model_name].columns[0]
        # valid_traits: trait IDs as strings
        valid_traits = pt2acc_dict[model_name].index.astype(str)
        # name_map: description -> description, for all valid traits
        name_map = {
            pt2acc_dict[model_name].at[pt, desc_col]: pt2acc_dict[model_name].at[pt, desc_col]
            for pt in valid_traits
        }
        # Only rename columns that exist in wide_bin
        col_rename = {k: v for k, v in name_map.items() if k in wide_bin.columns}
        wide_bin.rename(columns=col_rename, inplace=True)
        wide_bin = wide_bin.sort_index(axis=0).sort_index(axis=1)
        bin_fp = os.path.join(args.outdir, f"Traitar.binary.{model_name}.tsv.gz")
        wide_bin.to_csv(bin_fp, sep='\t', compression='gzip', index_label='sample')

    for model_name, prob_dict in all_prob_calls.items():
        wide_prob = pd.DataFrame(prob_dict)
        desc_col = pt2acc_dict[model_name].columns[0]
        valid_traits = pt2acc_dict[model_name].index.astype(str)
        name_map = {
            pt2acc_dict[model_name].at[pt, desc_col]: pt2acc_dict[model_name].at[pt, desc_col]
            for pt in valid_traits
        }
        col_rename = {k: v for k, v in name_map.items() if k in wide_prob.columns}
        wide_prob.rename(columns=col_rename, inplace=True)
        wide_prob = wide_prob.sort_index(axis=0).sort_index(axis=1)
        prob_fp = os.path.join(args.outdir, f"Traitar.prob.{model_name}.tsv.gz")
        wide_prob.to_csv(prob_fp, sep='\t', compression='gzip', index_label='sample')

    # Merge all binary calls into a dict of DataFrames
    merged_binary_frames = {}
    for model_name, binary_dict in all_binary_calls.items():
        merged_binary_frames[model_name] = pd.DataFrame(binary_dict)

    # Merge all probability calls into a dict of DataFrames
    merged_prob_frames = {}
    for model_name, prob_dict in all_prob_calls.items():
        merged_prob_frames[model_name] = pd.DataFrame(prob_dict)

    # Compute Traitar.original.tsv.gz if phypat and phypat_PGL exist
    if 'phypat' in merged_binary_frames and 'phypat_PGL' in merged_binary_frames:
        phypat_bin = merged_binary_frames.get('phypat')
        pgl_bin = merged_binary_frames.get('phypat_PGL')
        # Align indexes and columns
        common_index = phypat_bin.index.intersection(pgl_bin.index)
        common_cols = phypat_bin.columns.intersection(pgl_bin.columns)
        phypat_bin_aligned = phypat_bin.loc[common_index, common_cols]
        pgl_bin_aligned = pgl_bin.loc[common_index, common_cols]
        original_agg = (
            (phypat_bin_aligned.fillna(0).astype(int) > 0).astype(int) +
            (pgl_bin_aligned.fillna(0).astype(int) > 0).astype(int) * 2
        )
        original_agg = original_agg.sort_index(axis=0).sort_index(axis=1)
        original_agg.to_csv(
            os.path.join(args.outdir, "Traitar.original.tsv.gz"),
            sep='\t', compression='gzip', index_label='sample'
        )

    # Create Traitar.binary.tsv.gz: merged values set to 1 if > 0 in any model
    merged_binary_df = ((pd.concat(merged_binary_frames.values(), axis=1) > 0).astype(int).groupby(level=0, axis=1).mean() > 1).astype(int)
    merged_binary_df = merged_binary_df.sort_index(axis=0).sort_index(axis=1)
    merged_binary_df.to_csv(
        os.path.join(args.outdir, "Traitar.binary.tsv.gz"),
        sep='\t', compression='gzip', index_label='sample'
    )

    # Create Traitar.prob.tsv.gz: mean across all probability values
    merged_prob_df = pd.concat(merged_prob_frames.values(), axis=1).groupby(level=0, axis=1).mean()
    merged_prob_df = merged_prob_df.sort_index(axis=0).sort_index(axis=1)
    merged_prob_df.to_csv(
        os.path.join(args.outdir, "Traitar.prob.tsv.gz"),
        sep='\t', compression='gzip', index_label='sample'
    )
