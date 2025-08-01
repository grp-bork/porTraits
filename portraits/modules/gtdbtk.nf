process gtdbtk_classify {
    tag "${genome_id}"

    input:
    tuple val(genome_id), path(genome_fasta)
    path(gtdbtk_data)

    output:
    path("${genome_id}/gtdbtk") //, maxDepth: '2')

    script:
    """
    mkdir ${genome_id}/ gtdbtk/ genomes/

    if [[ "${genome_fasta}" == *".gz" ]]; then
		ln -sf ../${genome_fasta} genomes/${genome_id}.fna.gz
	else
		gzip -vc ${genome_fasta} > genomes/${genome_id}.fna.gz
	fi

    gtdbtk classify_wf --mash_db ./mash.db --cpus ${task.cpus} --pplacer_cpus ${task.cpus} --genome_dir ./genomes --out_dir gtdbtk --extension .fna.gz

    mv -v gtdbtk ${genome_id}/
    """
}
