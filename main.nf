include { recognise_genome } from "./portrait/modules/recognise"
// include { prodigal } from "./portrait/modules/prodigal"
include { gtdbtk_classify } from "./portrait/modules/gtdbtk"
include { genomespot } from "./portrait/modules/genomespot"

params.file_pattern = "**.{fna,fasta,fa,fna.gz,fasta.gz,fa.gz}"

workflow {

	genomes_ch = Channel
        .fromPath(params.input_dir + "/" + params.file_pattern)
        .map { fasta ->
            def genome_id = fasta.name.replaceAll(/\.(fa|fasta|fna)(\.gz)?/, "")
            return tuple(genome_id, fasta)
        }

	gtdbtk_classify(genomes_ch, params.gtdbtk_data)
	recognise_genome(genomes_ch, params.recognise_marker_genes)

	genomespot_input_ch = genomes_ch
		.join(recognise_genome.out.proteins, by: 0)

	genomespot(genomespot_input_ch)

	// prodigal(genomes_ch)


}