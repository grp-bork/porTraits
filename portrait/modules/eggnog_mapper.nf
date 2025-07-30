process eggnog_mapper {
	// container "quay.io/biocontainers/eggnog-mapper:2.1.12--pyhdfd78af_0"
	label "eggnog_mapper"
	tag "${genome_id}"
	cpus 16
	time {4.d * task.attempt}
	memory {64.GB * task.attempt}

	input:
	tuple val(genome_id), path(proteins)
	path(eggnog_db)

	output:
	tuple val(genome_id), path("${genome_id}/${genome_id}.emapper.annotations"), emit: eggnog

	script:
	"""
	mkdir -p ${genome_id}/
	

	emapper.py -i ${proteins} --data_dir ${eggnog_db} --output ${genome_id}/${genome_id} -m diamond --cpu $task.cpus --dmnd_algo 0
	"""

}


process emapper2matrix {
	tag "${genome_id}"

	input:
	tuple val(genome_id), path(emapper_output)
	path(pfam_clade_map)

	output:
	tuple val(genome_id), path("${genome_id}/e2m/*.KEGG_ko.tsv.gz"), emit: ko_matrix, optional: true
	tuple val(genome_id), path("${genome_id}/e2m/*.PFAMs.tsv.gz"), emit: pfam_matrix, optional: true

	script:
	"""
	mkdir -p ${genome_id}/em2
	emapper2matrix.py --input-file ${emapper_output} --pfam-map-file ${pfam_clade_map} --outdir ${genome_id}/e2m
	"""

}