process gtdbtk_classify {
    tag "${genome_id}"

    input:
    tuple val(genome_id), path(genome_fasta)
    path(gtdbtk_data)

    output:
    path("${genome_id}", maxDepth: '2')

    script:
    """
    mkdir ${genome_id} genomes

    if [[ "${genome_fasta}" == *".gz" ]]; then
		ln -sf ../${genome_fasta} genomes/${genome_id}.fna.gz
	else
		gzip -vc ${genome_fasta} > genomes/${genome_id}.fna.gz
	fi

    gtdbtk classify_wf --mash_db ./mash.db --cpus ${task.cpus} --pplacer_cpus ${task.cpus} --genome_dir ./genomes --out_dir ${genome_id} --extension .fna.gz
    """
}
