def METATRAITS_URL = "https://metatraits.embl.de/api/v1"

process metatraits_speci_call {
	input:
	tuple val(genome_id), val(speci)

	output:
	tuple val(genome_id), path("${genome_id}/metatraits/traits_from_speci.json"), emit: metatraits

	script:
	"""
	mkdir -p ${genome_id}/metatraits/

	taxid=\$(curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET ${METATRAITS_URL}/species_taxonomy/${speci} | grep -o '"species_tax_id":"[0-9]\+"' | cut -f 2 -d : | sed 's/"//g')
	
	curl -H "Accept: application/json" -H "Content-Type: application/text" -X GET https://metatraits.embl.de/api/v1/traits/taxonomy/\$speci -o ${genome_id}/metatraits/traits_from_speci.json
	"""
}