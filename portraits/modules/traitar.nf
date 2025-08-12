params.traitar_nvoters = 5

process traitar {
	tag "${genome_id}"
	label "tiny"

	input:
	tuple val(genome_id), path(pfam_matrix)
	path("traitar_models")

	output:
	tuple val(genome_id), path("${genome_id}/traitar/*.tsv.gz"), emit: predictions

	script:
	"""
	mkdir -p ${genome_id}/traitar/
	PFAM2Traitar.py --pfam-matrix ${pfam_matrix} --model-dir traitar_models --outdir ${genome_id}/traitar/ --voters ${params.traitar_nvoters}
	"""

}