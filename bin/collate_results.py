#!/usr/bin/env python3

import argparse


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--input_dir", "-i", type=str,)
	ap.add_argument("--output_dir", "-o", type=str,)
	args = ap.parse_args()

	


if __name__ == "__main__":
	main()