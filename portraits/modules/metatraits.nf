def METATRAITS_URL = "https://metatraits.embl.de/api/v1"

process metatraits_speci_call {
	// container "docker://quay.io/biocontainers/curl:7.45.0--2"
	// container "docker://registry.git.embl.org/schudoma/portraits_metatraits:latest"
	label "tiny"
	tag "Querying metatraits for ${speci}"


	input:
	val(speci)

	output:
	tuple val(speci), path("metatraits/${speci}.traits_from_speci.json"), emit: metatraits

	script:
	"""
	mkdir -p metatraits/

	metatraits_comm.py --speci ${speci} -o metatraits/${speci}.traits_from_speci.json	
	"""
	// taxid=\$(wget -O - ${METATRAITS_URL}/species_taxonomy/${speci} 2> /dev/null | grep -o '"species_tax_id":"[0-9]\\+"' | cut -f 2 -d : | sed 's/"//g')
	// wget -O ${genome_id}/metatraits/traits_from_speci.json ${METATRAITS_URL}/traits/taxonomy/\$taxid 2> /dev/null
	// taxid=\$(curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET ${METATRAITS_URL}/species_taxonomy/${speci} | grep -o '"species_tax_id":"[0-9]\\+"' | cut -f 2 -d : | sed 's/"//g')
	// curl -H "Accept: application/json" -H "Content-Type: application/text" -X GET https://metatraits.embl.de/api/v1/traits/taxonomy/\$taxid -o ${genome_id}/metatraits/traits_from_speci.json
}


process metatraits_taxon_call {
	label "tiny"
	tag "Querying metatraits for ${lineage}"

	input:
	tuple val(lineage), val(lineage_id)

	output:
	tuple val(lineage), val(lineage_id), path("metatraits/lineage/*.traits_from_lineage.json"), emit: metatraits
	path("metatraits/lineage/${lineage_id}.txt")

	script:
	"""
	mkdir -p metatraits/lineage

	metatraits_comm.py --lineage '${lineage}' -o metatraits/lineage/${lineage_id}.traits_from_lineage.json
	printf "%s\\t%s\\n" "${lineage_id}" "${lineage}" >> metatraits/lineage/${lineage_id}.txt
	"""
}