#!/usr/bin/env python3

import os
import glob
import pickle
import argparse
import pandas as pd

import sklearn
from packaging import version

# Ensure compatible scikit-learn version
required_version = "1.4.0"
if version.parse(sklearn.__version__) != version.parse(required_version):
    print(f"Warning: scikit-learn version {required_version} is required, but detected {sklearn.__version__}.")

def predict(pfam_fp, model_dir, outdir):
    # Detect gzip compression based on filename
    comp = 'gzip' if pfam_fp.endswith('.gz') else None
    # 1) Read & binarize the gzipped PFAM table (once)
    pf_df = pd.read_csv(pfam_fp,
                        sep="\t",
                        index_col=0,
                        compression=comp)
    X_full = (pf_df > 0).astype(int)

    # 2) Discover all your trait‐model dumps
    trait_files = glob.glob(os.path.join(model_dir, "*_data.p"))

    os.makedirs(outdir, exist_ok=True)
    successful = []

    # 3) Loop: load each model, predict probabilities and binary calls
    for trait_fp in trait_files:
        trait_name = os.path.basename(trait_fp).replace("_data.p", "")
        print(f"Starting prediction for {trait_name}...")
        try:
            with open(trait_fp, "rb") as handle:
                dump = pickle.load(handle)
            print("  Loading model and categories")
            clf = dump["model"]
            categories = dump["categories"]

            # align PFAM matrix to model features
            X = X_full.reindex(columns=categories, fill_value=0)

            # get probability of positive class
            # Convert to numpy array to avoid feature-name warning
            proba = clf.predict_proba(X.values)[:, 1]
            # print("  Computing probabilities and binary calls")
            # binary call at 0.5 threshold
            # binarized = (proba > 0.5).astype(int)

            # write probability output
            prob_fp = os.path.join(outdir, f"{trait_name}_predictions.tsv.gz")
            pd.DataFrame(proba, index=X.index, columns=[trait_name]).to_csv(
                prob_fp, sep="\t", index_label="MAG_id", compression="gzip"
            )

            # bin_fp = os.path.join(outdir, f"{trait_name}_predictions.binary.tsv.gz")
            # pd.DataFrame(binarized, index=X.index, columns=[trait_name]).to_csv(
            #     bin_fp, sep="\t", index_label="MAG_id", compression="gzip"
            # )

            print(f"  Results saved for {trait_name}:")
            print(f"    Probabilities → {prob_fp}")
            # print(f"    Binary calls → {bin_fp}")
            successful.append(trait_name)
        except Exception as e:
            print(f"Error processing {trait_name}: {e}")
    return successful



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict BacDive-AI traits from PFAM matrix")
    parser.add_argument("--pfam-matrix", required=True, help="Path to PFAMs_data.tsv.gz")
    parser.add_argument("--model-dir", required=True, help="Directory containing *_data.p model files")
    parser.add_argument("--outdir", dest="outdir", required=True, help="Directory for output prediction files")
    args = parser.parse_args()
    successful = predict(args.pfam_matrix, args.model_dir, args.outdir)

    # Merge all successful prediction files
    if successful:
        # Merge probability tables
        prob_dfs = []
        for trait in successful:
            prob_fp = os.path.join(args.outdir, f"{trait}_predictions.tsv.gz")
            try:
                df = pd.read_csv(prob_fp, sep='\t', index_col=0, compression='gzip')
                prob_dfs.append(df)
            except Exception as e:
                print(f"Warning: could not read {prob_fp}: {e}")
        if prob_dfs:
            merged_prob = pd.concat(prob_dfs, axis=1)
            merged_prob_fp = os.path.join(args.outdir, "BacDiveAI.prob.tsv.gz")
            merged_prob.to_csv(merged_prob_fp, sep='\t', compression='gzip')
            print(f"Merged probability table saved to {merged_prob_fp}")

        # Derive and save merged binary calls from merged probabilities
        merged_bin = (merged_prob > 0.5).astype(int)
        merged_bin_fp = os.path.join(args.outdir, "BacDiveAI.binary.tsv.gz")
        merged_bin.to_csv(merged_bin_fp, sep='\t', compression='gzip')
        print(f"Merged binary table saved to {merged_bin_fp}")
