include { recognise_genome } from "./portraits/modules/recognise"
include { gtdbtk_classify } from "./portraits/modules/gtdbtk"
include { genomespot } from "./portraits/modules/genomespot"
include { eggnog_mapper; emapper2matrix } from "./portraits/modules/eggnog_mapper"
include { micropherret } from "./portraits/modules/micropherret"
include { bacdive_ai } from "./portraits/modules/bacdive"
include { traitar } from "./portraits/modules/traitar"
include { metatraits_speci_call; metatraits_taxon_call } from "./portraits/modules/metatraits"
include { collate_results } from "./portraits/modules/collate"


params.file_pattern = "**.{fna,fasta,fa,fna.gz,fasta.gz,fa.gz}"


workflow {

	genomes_ch = Channel
        .fromPath(params.input_dir + "/" + params.file_pattern)
        .map { fasta ->
            def genome_id = fasta.name.replaceAll(/\.(fa(s(ta)?)?|fna)(\.gz)?$/, "")
            return tuple(genome_id, fasta)
        }

	all_results_ch = Channel.empty()

	// GTDBtk classification	
	gtdbtk_classify(genomes_ch, params.gtdbtk_data)

	all_results_ch = all_results_ch
		.mix(gtdbtk_classify.out.gtdb_taxonomy)

	// reCOGnise classification
	recognise_genome(genomes_ch, params.recognise_marker_genes)

	recognise_out_ch = recognise_genome.out.speci_status_ok
		.join(recognise_genome.out.genome_speci)
		.map { genome_id, status_ok, speci_file -> [ genome_id, speci_file ] }

	all_results_ch = all_results_ch
		.mix(recognise_out_ch)

	// metaTraits
	// recognise_out_ch.map { genome_id, speci_file -> [ genome_id, speci_file.text.replaceAll(/\n/, "") ]}

	if (params.query_metatraits && params.query_metatraits != "none") {


		if (params.query_metatraits == "NCBI" || params.query_metatraits == "both") {

			speci_ch = recognise_out_ch
				.map { genome_id, speci_file -> speci_file.text.replaceAll(/\n/, "") }
				.unique()
			metatraits_speci_call(speci_ch)
			all_results_ch = all_results_ch
				.mix(metatraits_speci_call.out.metatraits)

		}
		
		if (params.query_metatraits == "GTDB" || params.query_metatraits == "both") {

			def lineage_id = 0
			lineage_ch = gtdbtk_classify.out.gtdb_taxonomy
				.map { genome_id, file -> file.text }
				.splitCsv(header: true, sep: "\t")
				.map { row -> row.classification }
				.unique()
				.map { lineage -> [ lineage, lineage_id++ ]}
			
			lineage_ch.dump(pretty: true, tag: "lineage_ch")

			metatraits_taxon_call(lineage_ch)

			all_results_ch = all_results_ch
				.mix(metatraits_taxon_call.out.metatraits.map { lineage, lid, file -> [ lid, file ] } )
				.mix(metatraits_taxon_call.out.lineage_info.map { lineage, lid, file -> [ lid, file ] } )

		}

	}

	// genomeSPOT
	genomespot_input_ch = genomes_ch
		.join(recognise_genome.out.proteins, by: 0)

	genomespot(
		genomespot_input_ch,
		"${params.metatraits_models}/GenomeSPOT/models"
	)
	
	all_results_ch = all_results_ch
		.mix(genomespot.out.predictions)

	// emapper
	eggnog_mapper(
		recognise_genome.out.proteins,
		params.eggnog_db
	)

	emapper2matrix(
		eggnog_mapper.out.eggnog,
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
