params.recognise = [:]
params.recognise.marker_set = "motus"


process recognise {
	container "oras://registry.git.embl.de/schudoma/recognise-singularity/recognise-singularity:8b158eab"
	label "recognise"
	cpus 8
	memory {16.GB * task.attempt}
	time { 1.d * task.attempt }


	input:
	tuple val(speci), val(genome_id), path(genes), path(proteins)
	path(marker_genes_db)
	path(genes_db)
	path(db_credentials)
	
	output:
	tuple val(speci), val(genome_id), path("recognise/${genome_id}/${genome_id}.cogs.txt"), emit: cog_table
	tuple val(speci), val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.txt"), emit: genome_speci
	tuple val(speci), val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.status"), emit: speci_status
	tuple val(speci), val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.ffn.gz"), emit: speci_sequences, optional: true
	tuple val(speci), val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.status.OK"), emit: speci_status_ok, optional: true 

	script:
	"""
	recognise --marker_set ${params.recognise.marker_set} --genes ${genes} --proteins ${proteins} --cpus ${task.cpus} -o recognise/${genome_id} ${genome_id} \$(readlink ${marker_genes_db})
	"""

}

process recognise_genome {
	container "oras://registry.git.embl.de/schudoma/recognise-singularity/recognise-singularity:8b158eab"
	tag "${genome_id}"
	label "recognise"

	input:
	tuple val(genome_id), path(genome)
	path(marker_genes_db)
	
	
	output:
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.status.OK"), emit: speci_status_ok, optional: true 
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.cogs.txt"), emit: cog_table
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.txt"), emit: genome_speci
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.specI.status"), emit: speci_status
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.faa"), emit: proteins
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.ffn"), emit: genes
	tuple val(genome_id), path("recognise/${genome_id}/${genome_id}.gff"), emit: gff
	// tuple val(speci), val(genome_id), path("")			mv -v recognise/\$genome_id/\$genome_id.{faa,ffn,gff}  prodigal/\$genome_id/


	script:
	"""
	if [[ "${genome}" == *".gz" ]]; then
		gzip -dc ${genome} > genome_file
	else
		ln -sf ${genome} genome_file
	fi


	recognise --marker_set ${params.recognise.marker_set} --genome genome_file --cpus ${task.cpus} --with_gff -o recognise/${genome_id} ${genome_id} \$(readlink ${marker_genes_db})
	
	rm -fv genome_file
	"""
	// recognise --marker_set ${params.recognise.marker_set} --genome ${genome} --cpus ${task.cpus} --with_gff -o recognise/\$genome_id \$genome_id \$(readlink ${marker_genes_db})

}


process buffered_recognise {
	container "oras://registry.git.embl.de/schudoma/recognise-singularity/recognise-singularity:8b158eab"
	label "recognise"
	
	input:
	path(fasta)
	path(marker_genes_db)

	output:
	path("recognise/**.cogs.txt"), emit: cog_table
	path("recognise/**.specI.txt"), emit: genome_speci
	path("recognise/**.specI.status"), emit: speci_status
	path("recognise/**.specI.status.OK"), emit: speci_status_ok

	script:
	"""
	for protein_file in *.faa.gz; do
		genome_id=\$(basename \$protein_file .faa.gz)
		recognise --marker_set ${params.recognise.marker_set} --genes \$genome_id.ffn.gz --proteins \$protein_file --cpus ${task.cpus} -o recognise/\$genome_id \$genome_id \$(readlink ${marker_genes_db})
	done
	"""

}

process buffered_recognise_genome {
	container "oras://registry.git.embl.de/schudoma/recognise-singularity/recognise-singularity:8b158eab"
	label "recognise"

	input:
	path(fasta)
	path(marker_genes_db)
	val(file_suffix)

	output:
	path("recognise/**.cogs.txt"), emit: cog_table
	path("recognise/**.specI.txt"), emit: genome_speci
	path("recognise/**.specI.status"), emit: speci_status
	path("recognise/**.specI.status.OK"), emit: speci_status_ok
	path("prodigal/**.gz"), emit: prodigal_annotations

	script:
	"""
	for genome_file in ${fasta}; do
		genome_id=\$(basename \$genome_file ${file_suffix})
		mkdir -p prodigal/\$genome_id/

		if [[ "\$genome_file" == *".gz" ]]; then
			gzip -dc \$genome_file > \$(basename \$genome_file .gz)
		fi
		
		recognise --marker_set ${params.recognise.marker_set} --genome \$(basename \$genome_file .gz) --cpus ${task.cpus} --with_gff -o recognise/\$genome_id \$genome_id \$(readlink ${marker_genes_db})
		mv -v recognise/\$genome_id/\$genome_id.{faa,ffn,gff}  prodigal/\$genome_id/

		if [[ "\$genome_file" == *".gz" ]]; then
			rm -fv \$(basename \$genome_file .gz)
		fi

		gzip -v prodigal/\$genome_id/*
	done
	"""

}