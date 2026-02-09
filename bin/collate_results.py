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
		display_id = trait.lower().replace("*", "") if isinstance(trait, str) else "na"
		display_id = re.sub(r"[^a-z0-9]+", "-", display_id).strip("-")
		if display_id == "na":
			return "-"
		return f"{PortraitsCollator.METATRAITS_URL}/traits#{display_id}"

	@staticmethod
	def read_traits_json(f):
		with open(f, "rb") as _in:
			return json.load(_in)

	def harmonize(self, tool, trait):
		return self.traits_harmonized.get(tool, {}).get(trait)

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
					continue
				fn_match = re.match(r'(.+)\.genomespot\.predictions\.tsv', f.name)
				if fn_match:
					genome, *_ = fn_match.groups()
					d.setdefault("genomespot", {}).setdefault(genome, []).append(f)
					continue
				# IMCC31440b.gtdbtk.bac120.summary.tsv
				fn_match = re.match(r'(.+)\.gtdbtk\.(.+)\.summary\.tsv', f.name)
				if fn_match:
					genome, *_ = fn_match.groups()
					d.setdefault("gtdbtk", {}).setdefault(genome, []).append(f)
					continue
				fn_match = re.match(r'(.+)\.specI\.txt', f.name)
				if fn_match:
					genome, *_ = fn_match.groups()
					d.setdefault("recognise", {}).setdefault(genome, []).append(f)
					continue
				fn_match = re.match(r'([0-9]+)\.(traits_from_lineage\.json|txt)', f.name)
				if fn_match:
					lineage_id, *ltype = fn_match.groups()
					d.setdefault("metatraits_gtdb", {}).setdefault(lineage_id, [None, None])[ltype[0] == "txt"] = f
				fn_match = re.match(r'(specI_v4_[0-9]{5})\.(tax|traits_from_speci)\.json', f.name)
				if fn_match:
					speci, *ltype = fn_match.groups()
					d.setdefault("metatraits_ncbi", {}).setdefault(speci, [None, None])[ltype[0] == "tax"] = f

				# specI_v4_19275.tax.json  specI_v4_19275.traits_from_speci.json

		return d

	def process_predictor_outputs(self, tool, f_binary, f_prob):

		tool_version = self.versions.get(tool.lower())

		df_binary = pd.read_csv(f_binary, sep="\t", index_col=0,)
		df_prob = pd.read_csv(f_prob, sep="\t", index_col=0, header=0, names=df_binary.columns,)

		# print(df_binary)
		# print(df_prob)

		"""
		A. for Traitar calculate 'aerotolerant' = 1- 'Anaerobe'
B. for genomeSPOT use value, except 'oxygen' which is a bit stupid: the value is 'not tolerant' OR 'tolerant' and 'error' has the value for the probability so is never <0.5. This needs recoding with 1-probability if 'not tolerant'
C. for BacDive-AI, 'aerotolerant'  = 1-'anaerobic'
		"""

		trait_data = []
		pos_aerotolerant, pos_anaerobe = None, None
		for trait in df_binary.columns:
			feature = self.harmonize(tool.lower(), trait)
			tmeta = self.traits_info.get(feature, {})

			trait_data.append(
				(
					feature,
					tmeta.get("category"),
					tmeta.get("group1"),
					tmeta.get("group2"),
					tmeta.get("ontology"),
					PortraitsCollator.get_metatraits_link(feature),
				)
			)

			if feature == "obligate anaerobic":
				pos_anaerobe = len(trait_data) - 1
			elif feature == "aerotolerant":
				pos_aerotolerant = len(trait_data) - 1
			# print(*trait_data, sep="\n")

		probabilities, binaries = df_prob.iloc[0].tolist(), df_binary.iloc[0].tolist()
		
		tool_features = df_binary.columns.to_list()

		if tool.lower() in ("bacdiveai", "traitar") and pos_anaerobe is not None:
			if pos_aerotolerant is None:
				pos_aerotolerant = len(trait_data)
				tmeta = self.traits_info.get("aerotolerant", {})
				trait_data.append(
					(
						"aerotolerant",
						tmeta.get("category"),
						tmeta.get("group1"),
						tmeta.get("group2"),
						tmeta.get("ontology"),
						PortraitsCollator.get_metatraits_link("aerotolerant"),
					)
				)
				probabilities.append(None)
				binaries.append(None)
				tool_features.append("aerotolerant")
			
			probabilities[pos_aerotolerant] = 1 - probabilities[pos_anaerobe]
			binaries[pos_aerotolerant] = int(probabilities[pos_aerotolerant] > 0.5)


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
				"tool_feature": tool_features,  # df_binary.columns,
				"genome": df_binary.index[0],
				"value_probability": probabilities,  # df_prob.iloc[0].tolist(),
				"value_binary": binaries,  # df_binary.iloc[0].tolist(),
			}
		)

	def process_genomespot_outputs(self, f, genome):
		df = pd.read_csv(f, sep="\t", index_col=0,).transpose()
		values = df.iloc[0].to_list()
		errors = df.iloc[1].to_list()

		trait_data = []
		pos_oxygen = None
		for trait in df.columns:
			feature = self.harmonize("genomespot", trait)
			tmeta = self.traits_info.get(feature, {})
			if trait == "oxygen":
				pos_oxygen = len(trait_data)
			trait_data.append(
				[
					feature,
					tmeta.get("category"),
					tmeta.get("group1"),
					tmeta.get("group2"),
					tmeta.get("ontology"),
					PortraitsCollator.get_metatraits_link(feature),
					None,
				]
			)
	
		# for genomeSPOT use value, except 'oxygen' which is a bit stupid: 
		# the value is 'not tolerant' OR 'tolerant' and 'error' has the value for the probability so is never <0.5. 
		# This needs recoding with 1-probability if 'not tolerant'

		if pos_oxygen is not None:
			if values[pos_oxygen] == "not tolerant":
				values[pos_oxygen] = 1 - errors[pos_oxygen]
			else:
				values[pos_oxygen] = errors[pos_oxygen]
			trait_data[pos_oxygen][-1] = int(values[pos_oxygen] > 0.5)

		features, categories, group1, group2, ontology, links, binaries = zip(*trait_data)

		return pd.DataFrame(
			{
				"feature": features,
				"category": categories,
				"group1": group1,
				"group2": group2,
				"ontology": ontology,
				"trait_link": links,
				"tool": "genomespot",
				"tool_version": self.versions.get("genomespot"),
				"tool_feature": df.columns,  # df_binary.columns,
				"genome": genome,
				"value_probability": values,  # df_prob.iloc[0].tolist(),
				"value_binary": binaries,  # df_binary.iloc[0].tolist(),
			}
		)

def parse_taxonomy_data(gtdb=None, speci=None):
	tax_d = {}
	if gtdb:
		for genome, files in gtdb.items():
			with open(files[0], "rt") as _in:
				lineage = _in.readlines()[1].strip().split("\t")[1]
				tax_d.setdefault(genome, {})["gtdb"] = lineage
	if speci:
		for genome, files in speci.items():
			with open(files[0], "rt") as _in:
				tax_d.setdefault(genome, {})["speci"] = _in.read().strip()

	return pd.DataFrame(tax_d).transpose()

def parse_metatraits_summary(fn, lineage=None, species=None,):
	with open(fn, "rb") as _in:
		trait_data = []
		for trait in json.load(_in):			
			if trait.get("name"):

				perc_str = ";".join(
					f"{k}:{v}"
					for k, v in trait.get("percentages", {}).items()
				)

				trait_data.append(
					(
						trait.get("name"),
						trait.get("num_observations"),
						trait.get("unique_databases"),
						trait.get("majority_label"),
						perc_str,
					)
				)

	names, obs, dbs, majorities, percentages = zip(*trait_data)

	d = {}
	if lineage is not None:
		d["lineage"] = lineage
	elif species is not None:
		d["species"] = species[1]
		d["taxonomy_id"] = species[2]
		d["speci"] = species[0]

	d.update(
		{
			"name": names,
			"observations": obs,
   			"n_unique_databases": dbs,
			"majority_label": majorities,
			"percentages": percentages,
		}
	)

	return pd.DataFrame(d)








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


	data_frames = []
	for tool, genomes in results.items():

		if tool in ("metatraits_ncbi", "metatraits_gtdb", "gtdbtk", "recognise",):
			continue

		# print(tool)
		if tool == "genomespot":
			for genome, files in genomes.items():
				data_frames.append(pc.process_genomespot_outputs(files[0], genome))
		else:
			for genome, files in genomes.items():
				# print(tool, genome, files)
				data_frames.append(pc.process_predictor_outputs(tool, files["binary"], files["prob"]))


	if data_frames:
		tax_df = parse_taxonomy_data(gtdb=results.get("gtdbtk"), speci=results.get("recognise"))
		# tax_df.to_csv(f"{args.output_dir}/tax.tsv", sep="\t", index=False, na_rep="NA",)

		df = pd.concat(data_frames)

		df = pd.merge(df, tax_df, left_on="genome", right_index=True,)

		df.sort_values(by=["category", "group1", "group2", "feature", "tool",]).to_csv(f"{args.output_dir}/concat.tsv.gz", sep="\t", index=False, na_rep="NA",)

	if results.get("metatraits_gtdb"):
		data_frames = []
		# d.setdefault("metatraits_gtdb").setdefault(lineage_id, [None, None])[ltype[0] == "txt"] = f
		for lineage_id, files in results.get("metatraits_gtdb").items():

			traits_file, lineage_file = files
			with open(lineage_file, "rt") as _in:
				lineage = _in.read().strip().split("\t")[1]

			data_frames.append(parse_metatraits_summary(traits_file, lineage=lineage,))

			df = pd.concat(data_frames)

			df.to_csv(f"{args.output_dir}/metatraits_gtdb.tsv.gz", sep="\t", index=False, na_rep="NA",)

	if results.get("metatraits_ncbi"):
		data_frames = []
		for speci, files in results.get("metatraits_ncbi").items():

			traits_file, species_file = files
			with open(species_file, "rt") as _in:
				species_d = json.load(_in)

			#  {'species_name': 'Escherichia coli', 'species_tax_id': '562'})
			data_frames.append(parse_metatraits_summary(traits_file, species=(speci, species_d.get("species_name", "NA"), species_d.get("species_tax_id", "NA"))))

			df = pd.concat(data_frames)

			df.to_csv(f"{args.output_dir}/metatraits_ncbi.tsv.gz", sep="\t", index=False, na_rep="NA",)

	

	
	

if __name__ == "__main__":
	main()