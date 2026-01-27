#!/usr/bin/env python3

import argparse
import glob
import pathlib
import re


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--input_dir", "-i", type=str,)
	ap.add_argument("--output_dir", "-o", type=str,)
	args = ap.parse_args()

	d = {}

	# IMCC31440.MICROPHERRET.binary.tsv.gz
	for f in pathlib.Path(args.input_dir).iterdir():
		if f.is_file():
			rematch = re.match(r'(.+)\.(\w+)\.(binary|prob)(\.(\w+))?\.tsv.gz', f.name)
			if rematch:
				try:
					genome, tool, ctype, *subset = rematch.groups()
				except ValueError:
					continue
				print(genome, tool, ctype, "".join(subset[-1:]), sep="\t")
				if not subset:
					d.setdefault(tool, {}).setdefault(genome, {})[ctype] = f
	


if __name__ == "__main__":
	main()