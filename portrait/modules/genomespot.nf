process genomespot {

	tag "${genome_id}"


	input:
	tuple val(genome_id), path(genome_fasta), path(proteins)

	script:
	"""
	python -m genome_spot.genome_spot --models models \
    --contigs ${genome_fasta} \
    --proteins ${proteins} \
    --output ${genome_id}
	"""

}