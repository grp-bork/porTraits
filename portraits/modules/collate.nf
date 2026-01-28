process collate_results {
	label "tiny"
	tag "Collating..."

	input:
	path(files)
	path(traits_info)
	path(traits_harmonized)
	path(versions)

	output:
	path("collated/final_table.tsv")

	script:
	"""
	mkdir -p collated/
	touch collated/final_table.tsv
	collate_results.py -i . -o collated/ --traits_info ${traits_info} --traits_harmonized ${traits_harmonized} --versions ${versions}
	"""

	// ap.add_argument("--traits_info", type=str,)
	// ap.add_argument("--traits_harmonized", type=str,)
	// ap.add_argument("--versions", type=str,)
}