#!/usr/bin/env python3

import argparse
import glob
import json
import pathlib
import re

import pandas as pd



class PortraitsCollator:
	METATRAITS_URL = "https://metatraits.embl.de"

	def __init__(self, args):
		self.traits_info = PortraitsCollator.read_traits_json(args.traits_info)
		self.traits_harmonized = PortraitsCollator.read_traits_json(args.traits_harmonized)
		self.versions = PortraitsCollator.read_traits_json(args.versions)

	@staticmethod
	def get_metatraits_link(trait):
		display_id = trait.lower().replace("*", "")
		display_id = re.sub(r"[^a-z0-9]+", "-", display_id).strip("-")
		return f"{PortraitsCollator.METATRAITS_URL}/traits#{display_id}"

	@staticmethod
	def read_traits_json(f):
		with open(f, "rb") as _in:
			return json.load(_in)

	def harmonize(self, tool, trait):
		return self.harmonized_traits.get(tool, {}).get(trait, "NA")

	def scan_results_dir(self, results_dir):
		d = {}

		# IMCC31440.MICROPHERRET.binary.tsv.gz
		for f in pathlib.Path(results_dir).iterdir():
			if f.is_file():
				fn_match = re.match(r'(.+)\.(\w+)\.(binary|prob)(\.(\w+))?\.tsv.gz', f.name)
				if fn_match:
					try:
						genome, tool, ctype, *subset = fn_match.groups()
					except ValueError:
						continue
					print(genome, tool, ctype, subset[-1], sep="\t")
					if not subset[-1]:
						d.setdefault(tool, {}).setdefault(genome, {})[ctype] = f

		return d

	def process_predictor_outputs(self, tool, f_binary, f_prob):

		tool_version = self.versions.get(tool.lower(), "NA",)

		df_binary = pd.read_csv(f_binary, sep="\t", index_col=0,)
		df_prob = pd.read_csv(f_prob, sep="\t", index_col=0,)

		trait_data = []
		for trait in df_binary.columns:
			feature = self.harmonize(tool.lower(), trait)
			tmeta = self.traits_info.get(feature, {})

			trait_data.append(
				(
					feature,
					tmeta.get("category", "NA"),
					tmeta.get("group1", "NA"),
					tmeta.get("group2", "NA"),
					tmeta.get("ontology", "NA"),
					PortraitsCollator.get_metatraits_link(feature),
				)
			)

			features, categories, group1, group2, ontology, links = zip(*trait_data)
			
			return pd.DataFrame(
				{
					"feature": features,
					"category": categories,
					"group1": group1,
					"group2": group2,
					"ontology": ontology,
					"trait_link": links,
					"tool": tool,
					"tool_version": tool_version,
					"tool_feature": df_binary.columns,
					"genome": df_binary.index[0],
					"value_probability": df_prob.iloc[0].tolist(),
					"value_binary": df_binary.iloc[0].tolist(),
				}
			)






def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--input_dir", "-i", type=str,)
	ap.add_argument("--output_dir", "-o", type=str,)
	ap.add_argument("--traits_info", type=str,)
	ap.add_argument("--traits_harmonized", type=str,)
	ap.add_argument("--versions", type=str,)
	args = ap.parse_args()

	
	pc = PortraitsCollator(args)

	results = pc.scan_results_dir(args.input_dir)
	print(results)

	for tool, genomes in results.items():
		print(tool)
		for genome, files in genomes.items():
			print(genome, files)
			df = pc.process_predictor_outputs(tool, files["binary"], files["prob"])
			print(df)

	
	

if __name__ == "__main__":
	main()