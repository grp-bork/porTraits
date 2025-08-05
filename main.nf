include { recognise_genome } from "./portraits/modules/recognise"
include { gtdbtk_classify } from "./portraits/modules/gtdbtk"
include { genomespot } from "./portraits/modules/genomespot"
include { eggnog_mapper; emapper2matrix } from "./portraits/modules/eggnog_mapper"
include { micropherret } from "./portraits/modules/micropherret"
include { bacdive_ai } from "./portraits/modules/bacdive"
include { traitar } from "./portraits/modules/traitar"
include { metatraits_speci_call } from "./portraits/modules/metatraits"

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

	metatraits_speci_call_ch = recognise_genome.out.speci_status_ok
		.join(recognise_genome.out.genome_speci)
		.map { genome_id, status_ok, speci_file -> [genome_id, speci_file.text ] }

	metatraits_speci_call(metatraits_speci_call_ch)

	genomespot_input_ch = genomes_ch
		.join(recognise_genome.out.proteins, by: 0)

	genomespot(
		genomespot_input_ch,
		"${params.metatraits_models}/GenomeSPOT/models"
	)

	eggnog_mapper(
		recognise_genome.out.proteins,
		params.eggnog_db
	)

	emapper2matrix(
		eggnog_mapper.out.eggnog,
		params.pfam_clade_map
	)

	micropherret(
		emapper2matrix.out.ko_matrix,
		"${params.metatraits_models}/MICROPHERRET"
	)

	bacdive_ai(
		emapper2matrix.out.pfam_matrix,
		"${params.metatraits_models}/BacDive-AI/models"
	)

	traitar(
		emapper2matrix.out.pfam_matrix,
		"${params.metatraits_models}/Traitar/"
	)

}
