process bacdive_ai {
	tag "${genome_id}"

	input:
	tuple val(genome_id), path(pfam_matrix)
	path(bacdive_ai_models)

	script:
	"""
	mkdir -p bacdive_ai/${genome_id}
	PFAM2BacDive-AI.py --pfam-matrix ${pfam_matrix} --model-dir ${bacdive_ai_models} --outdir bacdive_ai/${genome_id}
	"""


}