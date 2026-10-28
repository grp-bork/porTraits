include { recognise_genome } from "../modules/recognise"
include { gtdbtk_classify } from "../modules/gtdbtk"
include { metatraits_speci_call; metatraits_taxon_call } from "../modules/metatraits"


workflow portraits_taxonomy {

	take:
		genomes_ch
	
	main:
		tax_results_ch = Channel.empty()

		// GTDBtk classification	
		gtdbtk_classify(genomes_ch, params.gtdbtk_data)

		tax_results_ch = tax_results_ch.mix(gtdbtk_classify.out.gtdb_taxonomy)

		// reCOGnise classification
		recognise_genome(genomes_ch, params.recognise_marker_genes)

		recognise_out_ch = recognise_genome.out.speci_status_ok
			.join(recognise_genome.out.genome_speci)
			.map { genome_id, status_ok, speci_file -> [ genome_id, speci_file ] }

		tax_results_ch = tax_results_ch.mix(recognise_out_ch)

		// Query metatraits reference data (if required)
		if (params.query_metatraits && params.query_metatraits != "none") {

			if (params.query_metatraits == "NCBI" || params.query_metatraits == "both") {

				speci_ch = recognise_out_ch
					.map { genome_id, speci_file -> speci_file.text.replaceAll(/\n/, "") }
					.unique()
				metatraits_speci_call(speci_ch)
				tax_results_ch = tax_results_ch
					.mix(metatraits_speci_call.out.metatraits)
					.mix(metatraits_speci_call.out.tax_info)

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

				tax_results_ch = tax_results_ch
					.mix(metatraits_taxon_call.out.metatraits.map { lineage, lid, file -> [ lid, file ] } )
					.mix(metatraits_taxon_call.out.lineage_info.map { lineage, lid, file -> [ lid, file ] } )

			}

		}

	emit:
		results = tax_results_ch
		proteins = recognise_genome.out.proteins

}