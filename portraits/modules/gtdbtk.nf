process gtdbtk_classify {
    tag "${genome_id}"
    label "small"

    input:
    tuple val(genome_id), path(genome_fasta)
    path(gtdbtk_data)

    output:
    path("${genome_id}/gtdbtk") //, maxDepth: '2')
    tuple val(genome_id), path("${genome_id}/gtdbtk/classify/${genome_id}.gtdbtk.*.summary.tsv"), emit: gtdb_taxonomy

    script:

    def mash_db = (params.mashdb_required) ? "--mash_db ./mash.db" : ""

    """
    mkdir ${genome_id}/ gtdbtk/ genomes/

    if [[ "${genome_fasta}" == *".gz" ]]; then
		ln -sf ../${genome_fasta} genomes/${genome_id}.fna.gz
	else
		gzip -vc ${genome_fasta} > genomes/${genome_id}.fna.gz
	fi

    gtdbtk classify_wf ${mash_db} --cpus ${task.cpus} --pplacer_cpus ${task.cpus} --genome_dir ./genomes --out_dir gtdbtk --extension .fna.gz

    res=\$(find gtdbtk -name 'gtdbtk.*.summary.tsv')
    if [[ -z \$res ]]; then touch gtdbtk/gtdbtk.no.summary.tsv; fi

    mv -v gtdbtk ${genome_id}/
    find ${genome_id} -type f -name 'gtdbtk.*.summary.tsv' | xargs -I{} sh -c 'ln -sf \$(basename {}) ${genome_id}.\$(basename {})'

    """
}
