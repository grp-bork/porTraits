params.recognise = [:]
params.recognise.marker_set = "motus"


process recognise_genome {
	container "oras://registry.git.embl.de/schudoma/recognise-singularity/recognise-singularity:8b158eab"
	tag "${genome_id}"
	label "recognise"
	label "small"

	input:
	tuple val(genome_id), path(genome)
	path(marker_genes_db)
	
	
	output:
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.specI.status.OK"), emit: speci_status_ok, optional: true 
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.cogs.txt"), emit: cog_table
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.specI.txt"), emit: genome_speci
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.specI.status"), emit: speci_status
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.faa"), emit: proteins
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.ffn"), emit: genes
	tuple val(genome_id), path("${genome_id}/recognise/${genome_id}.gff"), emit: gff

	script:
	"""
	if [[ "${genome}" == *".gz" ]]; then
		gzip -dc ${genome} > genome_file
	else
		ln -sf ${genome} genome_file
	fi

	recognise --marker_set ${params.recognise.marker_set} --genome genome_file --cpus ${task.cpus} --with_gff -o ${genome_id}/recognise ${genome_id} \$(readlink ${marker_genes_db})
	
	rm -fv genome_file
	"""

}
