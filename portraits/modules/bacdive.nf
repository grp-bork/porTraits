process bacdive_ai {
	label "tiny"

	tag "${genome_id}"

	input:
	tuple val(genome_id), path(pfam_matrix)
	path(bacdive_ai_models)

	output:
	tuple val(genome_id), path("${genome_id}/bacdive_ai/*.tsv.gz"), emit: predictions

	script:
	"""
	mkdir -p ${genome_id}/bacdive_ai/
	PFAM2BacDive-AI.py --pfam-matrix ${pfam_matrix} --model-dir ${bacdive_ai_models} --outdir ${genome_id}/bacdive_ai

	find ${genome_id}/ -type f | xargs -I{} sh -c 'mv {} \$(dirname {})/${genome_id}.\$(basename {})'
	"""

}