include { recognise_genome } from "./portrait/modules/recognise"
include { gtdbtk_classify } from "./portrait/modules/gtdbtk"
include { genomespot } from "./portrait/modules/genomespot"
include { eggnog_mapper; emapper2matrix } from "./portrait/modules/eggnog_mapper"
include { micropherret } from "./portrait/modules/micropherret"
include { bacdive_ai } from "./portrait/modules/bacdive"
include { traitar } from "./portrait/modules/traitar"

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

	// genomespot(genomespot_input_ch)

	eggnog_mapper(recognise_genome.out.proteins, params.eggnog_db)
	emapper2matrix(eggnog_mapper.out.eggnog, params.pfam_clade_map)

	micropherret(emapper2matrix.out.ko_matrix, params.micropherret_models)
	bacdive_ai(emapper2matrix.out.pfam_matrix, params.bacdive_ai_models)
	traitar(emapper2matrix.out.pfam_matrix, params.traitar_models)

}