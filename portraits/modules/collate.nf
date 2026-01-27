process collate_results {
	label "tiny"

	input:
	path(files)

	output:
	path("collated/final_table.tsv")

	script:
	"""
	mkdir -p collated/
	touch collated/final_table.tsv
	"""
}