process genomespot {

	tag "${genome_id}"


	input:
	tuple val(genome_id), path(genome_fasta), path(proteins)
	path(genomespot_models)

	script:
	"""
	python -m genome_spot.genome_spot \
	--models ${genomespot_models} \
    --contigs ${genome_fasta} \
    --proteins ${proteins} \
    --output ${genome_id}
	"""

}