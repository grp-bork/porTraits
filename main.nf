include { recognise_genome } from "./portraits/modules/recognise"
include { gtdbtk_classify } from "./portraits/modules/gtdbtk"
include { genomespot } from "./portraits/modules/genomespot"
include { eggnog_mapper; emapper2matrix } from "./portraits/modules/eggnog_mapper"
include { micropherret } from "./portraits/modules/micropherret"
include { bacdive_ai } from "./portraits/modules/bacdive"
include { traitar } from "./portraits/modules/traitar"
include { metatraits_speci_call; metatraits_taxon_call } from "./portraits/modules/metatraits"
include { collate_results } from "./portraits/modules/collate"

include { portraits_taxonomy } from "./portraits/workflows/taxonomy"

params.file_pattern = "**.{fna,fasta,fa,fna.gz,fasta.gz,fa.gz}"

genomes_ch = Channel
				.fromPath(params.input_sheet)
        		.splitCsv(sep: '\t', header: ["speci", "genome_id", "genome", "proteins", "genes", "gff", "emapper"])
				.map { gdata -> [gdata.speci, gdata.genome_id, gdata] }


workflow {

	proteins_ch = Channel.empty()
	emapper_ch = Channel.empty()
	genomes_ch = Channel.empty()

	if (params.samplesheet) {
		data_ch = Channel
			.fromPath(params.samplesheet)
			.splitCsv(sep: '\t', header: [ "genome_id", "speci", "gtdbtk", "genome", "proteins", "emapper" ])
		
		proteins_ch = data_ch
			.map { gdata -> [ gdata.genome_id, gdata.proteins ] }
		
		emapper_ch = data_ch
			.map { gdata -> [ gdata.genome_id, gdata.emapper ] }
			.filter { it -> it[1] != null }

		genomes_ch = data_ch
			.map { gdata -> [ gdata.genome_id, gdata.genome ] }


	} else {
		genomes_ch = Channel
			.fromPath(params.input_dir + "/" + params.file_pattern)
			.map { fasta ->
				def genome_id = fasta.name.replaceAll(/\.(fa(s(ta)?)?|fna)(\.gz)?$/, "")
				return tuple(genome_id, fasta)
			}
	}


	all_results_ch = Channel.empty()

	if (!params.skip_taxonomy) { 
		portraits_taxonomy(genomes_ch)
		all_results_ch = all_results_ch
			.mix(portraits_taxonomy.out.results)
		if (!params.samplesheet) {
			proteins_ch = portraits_taxonomy.out.proteins
		}
	}

	// genomeSPOT
	genomespot_input_ch = genomes_ch.join(proteins_ch, by: 0)

	genomespot(
		genomespot_input_ch,
		"${params.metatraits_models}/GenomeSPOT/models"
	)
	
	all_results_ch = all_results_ch
		.mix(genomespot.out.predictions)

	
	if (!params.skip_emapper) {
		// emapper
		eggnog_mapper(
			recognise_genome.out.proteins,
			params.eggnog_db
		)
		emapper_ch = eggnog_mapper.out.eggnog
	}

	emapper2matrix(
		emapper_ch,
		params.pfam_clade_map
	)

	all_results_ch = all_results_ch
		.mix(emapper2matrix.out.ko_matrix)
		.mix(emapper2matrix.out.pfam_matrix)


	// micropherret
	micropherret(
		emapper2matrix.out.ko_matrix,
		"${params.metatraits_models}/MICROPHERRET"
	)

	all_results_ch = all_results_ch
		.mix(micropherret.out.predictions)

	// bacdive-ai
	bacdive_ai(
		emapper2matrix.out.pfam_matrix,
		"${params.metatraits_models}/BacDive-AI/models"
	)

	all_results_ch = all_results_ch
		.mix(bacdive_ai.out.predictions)

	// Traitar
	traitar(
		emapper2matrix.out.pfam_matrix,
		"${params.metatraits_models}/Traitar/"
	)

	all_results_ch = all_results_ch
		.mix(traitar.out.predictions)

	collate_results(
		all_results_ch
			.map { genome_id, files -> [files].flatten() }
			.collect(),
		"${projectDir}/assets/traits_info.json",
		"${projectDir}/assets/traits_harmonized.json",
		"${projectDir}/assets/versions.json"

	)

}
