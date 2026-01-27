process genomespot {
	label "tiny"
	tag "${genome_id}"


	input:
	tuple val(genome_id), path(genome_fasta), path(proteins)
	path(genomespot_models)

	output:
	tuple val(genome_id), path("${genome_id}/genomespot/*.predictions.tsv"), emit: predictions

	script:
	"""
	mkdir -p ${genome_id}/genomespot/

	python -m genome_spot.genome_spot \
	--models ${genomespot_models} \
    --contigs ${genome_fasta} \
    --proteins ${proteins} \
    --output ${genome_id}/genomespot/${genome_id}.genomespot
	"""

}