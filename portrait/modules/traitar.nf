params.traitar_nvoters = 5

process traitar {
	tag "${genome_id}"

	input:
	tuple val(genome_id), path(pfam_matrix)

	script:
	"""
	mkdir -p traitar/${genome_id}/
	PFAM2Traitar.py --pfam-matrix ${pfam_matrix} --model-dir ${traitar_models} --outdir traitar/${genome_id} --voters ${params.traitar_nvoters}
	"""

}