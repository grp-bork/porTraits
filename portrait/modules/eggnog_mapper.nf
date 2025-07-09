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
	// mkdir eggnog_db_copy
	// ln -sf \$(readlink eggnog_db)/eggnog_proteins.dmnd eggnog_db_copy/
	// ln -sf \$(readlink eggnog_db)/eggnog.taxa.db eggnog_db_copy/
	// ln -sf \$(readlink eggnog_db)/eggnog.taxa.db.traverse.pkl eggnog_db_copy/
	// cp -v eggnog_db/eggnog.db eggnog_db_copy/
	"""
	mkdir -p ${genome_id}/
	

	emapper.py -i ${proteins} --data_dir ${eggnog_db} --output ${genome_id}/${genome_id} -m diamond --cpu $task.cpus --dmnd_algo 0 --pfam_realign realign
	"""
	// rm -rvf eggnog_db_copy
}


process emapper2matrix {
	tag "${genome_id}"

	input:
	tuple value(genome_id), path(emapper_output)
	path(pfam_clade_map)

	script:
	"""
	mkdir -p e2m/${genome_id}
	emapper2matrix.py --input-file ${emapper_output} --pfam-map-file ${pfam_clade_map} --outdir e2m/${genome_id}
	"""

}