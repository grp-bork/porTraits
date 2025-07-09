#!/usr/bin/env python3

# Patch sklearn tree NODE_DTYPE for compatibility with models pickled under older sklearn
import numpy as np
import sklearn.tree._tree as _tree
# Patch sklearn tree NODE_DTYPE for compatibility with models pickled under older sklearn
_tree.TREE_DTYPE = np.dtype({
    'names': [
        'left_child', 'right_child', 'feature', 'threshold',
        'impurity', 'n_node_samples', 'weighted_n_node_samples',
        'missing_go_to_left'
    ],
    'formats': ['<i8', '<i8', '<i8', '<f8', '<f8', '<i8', '<f8', 'u1'],
    'offsets': [0, 8, 16, 24, 32, 40, 48, 56],
    'itemsize': 64
})

import os
import sys
import argparse
import pandas as pd
import numpy as np
from sklearn.metrics import matthews_corrcoef, f1_score, confusion_matrix, accuracy_score, roc_auc_score, jaccard_score, zero_one_loss, hamming_loss
from keras.models import load_model
from pickle import load as pkl_load
import keras.backend as K
import tensorflow as tf
# suppress tf.function retracing warnings
tf.get_logger().setLevel('ERROR')

def matthews_correlation_coefficient(y_true, y_pred):
    tp = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    tn = K.sum(K.round(K.clip((1 - y_true) * (1 - y_pred), 0, 1)))
    fp = K.sum(K.round(K.clip((1 - y_true) * y_pred, 0, 1)))
    fn = K.sum(K.round(K.clip(y_true * (1 - y_pred), 0, 1)))
    num = tp * tn - fp * fn
    den = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    return num / K.sqrt(den + K.epsilon())

def get_validation_set(to_validate, training_set):
    training_kos = training_set.columns
    validation_kos = to_validate.columns
    common = set(training_kos).intersection(validation_kos)
    if not common:
        print('No common KOs between validation set and training set')
        return None

    common = list(common)
    print(f'{len(common)} common KOs')
    common_table = to_validate[common]

    to_remove = set(validation_kos) - set(training_kos)
    print(f'{len(to_remove)} KOs present in validation but not in training — will be removed')
    missing = list(set(training_kos) - set(validation_kos))
    print(f'{len(missing)} KOs missing from validation — will be zero-filled')
    missed = pd.DataFrame(0, index=to_validate.index, columns=missing)

    to_submit = pd.concat([common_table, missed], axis=1)
    to_submit = to_submit[training_kos]  # reorder columns
    print(f'Shape of training set: {training_set.shape}, validation set after alignment: {to_submit.shape}')

    if list(to_submit.columns) != list(training_kos):
        print('ERROR: column alignment mismatch')
        return None
    return to_submit

def predict(classes, ko_validation, model_dir, outdir):
    keras_traits = {
        "anoxygenic_photoautotrophy_Fe_oxidizing",
        "dark_sulfite_oxidation",
        "oil_bioremediation",
        "dark_sulfur_oxidation",
        "dark_thiosulfate_oxidation",
        "anoxygenic_photoautotrophy_S_oxidizing"
    }

    os.makedirs(outdir, exist_ok=True)
    successful = []
    for c in classes[::-1]:
        try:
            out_file = os.path.join(outdir, f"{c}.tsv.gz")
            if os.path.exists(out_file):
                print(f'File {out_file} already exists, skipping')
                continue

            print(f'Starting prediction for {c}...')
            if c in keras_traits:
                model_path = os.path.join(model_dir, f"{c}.mdl_wts.hdf5")
                print('  Loading Keras model:', model_path)
                modelo = load_model(model_path,
                                    compile=True,
                                    custom_objects={"matthews_correlation_coefficient": matthews_correlation_coefficient})
                scaler = pkl_load(open(os.path.join(model_dir, f"scaler_{c}.sav"), "rb"))
                to_validate_norm = scaler.transform(ko_validation)
                probs = modelo.predict(to_validate_norm).flatten()
                pred = (probs > 0.5).astype(int).tolist()
            else:
                model_path = os.path.join(model_dir, f"model_{c}.sav")
                print('  Loading model:', model_path)
                model = pkl_load(open(model_path, "rb"))
                scaler = pkl_load(open(os.path.join(model_dir, f"scaler_{c}.sav"), "rb"))
                to_validate_norm = scaler.transform(ko_validation)
                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(to_validate_norm)[:, 1]
                elif hasattr(model, "decision_function"):
                    raw = model.decision_function(to_validate_norm)
                    probs = 1 / (1 + np.exp(-raw))
                else:
                    probs = model.predict(to_validate_norm)
                pred = (probs > 0.5).astype(int)

            # Output only the probability for this trait
            results_df = pd.DataFrame(probs, index=ko_validation.index, columns=[f"{c}_prob"])
            results_df.to_csv(out_file, sep='\t', compression='gzip')
            print(f'  Results saved to {out_file}')
            successful.append(c)
        except Exception as e:
            print(f"Error predicting {c}: {e}")
    return successful

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KO2MICROPHERRET: predict microbial traits from KO presence/absence")
    parser.add_argument("--ko-matrix", required=True,
                        help="Path to KO matrix file (tab- or comma-separated, gzip OK), indexed by genome/sample")
    parser.add_argument("--model-dir", required=True,
                        help="Root directory containing 'saved_models/' and 'matrix/genome_ko_all.csv'")
    parser.add_argument("--outdir", required=True,
                        help="Directory to write trait prediction files")
    args = parser.parse_args()

    # Load training dataset
    train_path = os.path.join(args.model_dir, "matrix", "genome_ko_all.csv")
    if not os.path.isfile(train_path):
        print(f"Error: training matrix not found at {train_path}")
        sys.exit(1)
    training_dataset = pd.read_csv(train_path).set_index("Genome").drop("Species", axis=1)

    # Load user KO matrix
    ko_path = args.ko_matrix
    try:
        user_dataset = pd.read_csv(ko_path, sep="\t", index_col=0, compression="infer")
    except Exception:
        user_dataset = pd.read_csv(ko_path, index_col=0)

    # Remove 'ko:' prefix from column names
    user_dataset.columns = user_dataset.columns.str.replace(r"^ko:", "", regex=True)

    # Align to training set
    user_validated = get_validation_set(user_dataset, training_dataset)
    if user_validated is None:
        sys.exit(1)

    # Define trait classes
    classes = [
        'anoxygenic_photoautotrophy_Fe_oxidizing', 'oil_bioremediation', 'dark_sulfite_oxidation', 'arsenate_respiration',
        'manganese_respiration', 'dark_sulfur_oxidation', 'knallgas_bacteria', 'reductive_acetogenesis', 'dark_iron_oxidation',
        'dark_thiosulfate_oxidation', 'chlorate_reducers', 'iron_respiration', 'anoxygenic_photoautotrophy_H2_oxidizing',
        'nitrate_denitrification', 'chitinolysis', 'aerobic_anoxygenic_phototrophy', 'denitrification', 'dissimilatory_arsenate_reduction',
        'dark_sulfide_oxidation', 'ureolysis', 'cellulolysis', 'thiosulfate_respiration', 'nitrous_oxide_denitrification',
        'plastic_degradation', 'sulfur_respiration', 'aromatic_hydrocarbon_degradation', 'acetoclastic_methanogenesis', 'xylanolysis',
        'sulfite_respiration', 'fumarate_respiration', 'dark_hydrogen_oxidation', 'nitrification', 'methanol_oxidation', 'sulfate_respiration',
        'dark_oxidation_of_sulfur_compounds', 'nitrite_denitrification', 'arsenate_detoxification', 'anoxygenic_photoautotrophy_S_oxidizing',
        'nitrate_respiration', 'nitrite_respiration', 'aromatic_compound_degradation', 'nitrate_ammonification', 'ligninolysis',
        'nitrite_ammonification', 'phototrophy', 'respiration_of_sulfur_compounds', 'anoxygenic_photoautotrophy', 'methylotrophy',
        'nitrogen_fixation', 'invertebrate_parasites', 'nitrogen_respiration', 'photoheterotrophy', 'chemoheterotrophy', 'nitrate_reduction',
        'aerobic_ammonia_oxidation', 'predatory_or_exoparasitic', 'methanogenesis_using_formate', 'plant_pathogen',
        'human_pathogens_meningitis', 'human_pathogens_gastroenteritis', 'hydrocarbon_degradation', 'manganese_oxidation',
        'animal_parasites_or_symbionts', 'human_pathogens_all', 'photoautotrophy', 'human_pathogens_septicemia', 'aerobic_chemoheterotrophy',
        'human_associated', 'aliphatic_non_methane_hydrocarbon_degradation', 'human_pathogens_pneumonia', 'fermentation',
        'human_pathogens_diarrhea', 'mammal_gut', 'methanotrophy', 'human_gut', 'intracellular_parasites', 'methanogenesis_by_CO2_reduction_with_H2',
        'methanogenesis_by_disproportionation_of_methyl_groups', 'methanogenesis_by_reduction_of_methyl_compounds_with_H2',
        'hydrogenotrophic_methanogenesis', 'oxygenic_photoautotrophy', 'aerobic_nitrite_oxidation', 'methanogenesis',
        'arsenite_oxidation_detoxification', 'arsenite_oxidation_energy_yielding', 'fish_parasites', 'dissimilatory_arsenite_oxidation',
        'photosynthetic_cyanobacteria', 'human_pathogens_nosocomia'
    ]

    save_models_dir = os.path.join(args.model_dir, "saved_models")
    successful = predict(classes, user_validated, save_models_dir, args.outdir)
    # Merge all successful prediction files
    if successful:
        # Merge probability tables
        prob_dfs = []
        for c in successful:
            fpath = os.path.join(args.outdir, f"{c}.tsv.gz")
            try:
                df = pd.read_csv(fpath, sep='\t', index_col=0, compression='gzip')
                prob_dfs.append(df)
            except Exception as e:
                print(f"Warning: could not read {fpath}: {e}")
        if prob_dfs:
            merged_prob = pd.concat(prob_dfs, axis=1)
            out_prob = os.path.join(args.outdir, "MICROPHERRET.prob.tsv.gz")
            merged_prob.to_csv(out_prob, sep='\t', compression='gzip')
            print(f"Merged probability table saved to {out_prob}")

            # Derive and save binary calls at 0.5 threshold
            merged_bin = (merged_prob > 0.5).astype(int)
            # Rename columns to drop "_prob"
            merged_bin.columns = [col.replace("_prob", "") for col in merged_bin.columns]
            out_bin = os.path.join(args.outdir, "MICROPHERRET.binary.tsv.gz")
            merged_bin.to_csv(out_bin, sep='\t', compression='gzip')
            print(f"Merged binary table saved to {out_bin}")