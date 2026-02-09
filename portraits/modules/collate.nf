
def metatraits_gtdb_required = (params.query_metatraits == "GTDB" || params.query_metatraits == "both")
def metatraits_ncbi_required = (params.query_metatraits == "NCBI" || params.query_metatraits == "both")

process collate_results {
	label "tiny"
	tag "Collating..."

	input:
	path(files)
	path(traits_info)
	path(traits_harmonized)
	path(versions)

	output:
	path("collated/portraits_results.tsv.gz"), emit: portraits_table
	path("collated/metatraits_gtdb.tsv.gz"), emit: metatraits_gtdb, optional: !metatraits_gtdb_required
	path("collated/metatraits_ncbi.tsv.gz"), emit: metatraits_ncbi, optional: !metatraits_ncbi_required


	script:
	"""
	mkdir -p collated/
	collate_results.py -i . -o collated/ --traits_info ${traits_info} --traits_harmonized ${traits_harmonized} --versions ${versions}
	"""
}