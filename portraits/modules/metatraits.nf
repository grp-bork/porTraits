def METATRAITS_URL = "https://metatraits.embl.de/api/v1"

process metatraits_speci_call {
	// container "docker://quay.io/biocontainers/curl:7.45.0--2"
	// container "docker://registry.git.embl.org/schudoma/portraits_metatraits:latest"
	label "tiny"


	input:
	tuple val(genome_id), val(speci)

	output:
	tuple val(genome_id), path("${genome_id}/metatraits/${genome_id}.traits_from_speci.json"), emit: metatraits

	script:
	"""
	mkdir -p ${genome_id}/metatraits/

	metatraits_comm.py --speci ${speci} -o ${genome_id}/metatraits/${genome_id}.traits_from_speci.json
	"""
	// taxid=\$(wget -O - ${METATRAITS_URL}/species_taxonomy/${speci} 2> /dev/null | grep -o '"species_tax_id":"[0-9]\\+"' | cut -f 2 -d : | sed 's/"//g')
	// wget -O ${genome_id}/metatraits/traits_from_speci.json ${METATRAITS_URL}/traits/taxonomy/\$taxid 2> /dev/null
	// taxid=\$(curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET ${METATRAITS_URL}/species_taxonomy/${speci} | grep -o '"species_tax_id":"[0-9]\\+"' | cut -f 2 -d : | sed 's/"//g')
	// curl -H "Accept: application/json" -H "Content-Type: application/text" -X GET https://metatraits.embl.de/api/v1/traits/taxonomy/\$taxid -o ${genome_id}/metatraits/traits_from_speci.json
}