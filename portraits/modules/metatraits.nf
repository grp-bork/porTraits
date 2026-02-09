def METATRAITS_URL = "https://metatraits.embl.de/api/v1"

process metatraits_speci_call {
	label "tiny"
	tag "Querying metatraits for ${speci}"

	input:
	val(speci)

	output:
	tuple val(speci), path("metatraits/${speci}.traits_from_speci.json"), emit: metatraits
	tuple val(speci), path("metatraits/${speci}.tax.json"), emit: tax_info

	script:
	"""
	mkdir -p metatraits/

	metatraits_comm.py --speci ${speci} -o metatraits/${speci}
	"""
}


process metatraits_taxon_call {
	label "tiny"
	tag "Querying metatraits for ${lineage}"

	input:
	tuple val(lineage), val(lineage_id)

	output:
	tuple val(lineage), val(lineage_id), path("metatraits/lineage/*.traits_from_lineage.json"), emit: metatraits
	tuple val(lineage), val(lineage_id), path("metatraits/lineage/${lineage_id}.txt"), emit: lineage_info

	script:
	"""
	mkdir -p metatraits/lineage

	metatraits_comm.py --lineage '${lineage}' -o metatraits/lineage/${lineage_id}
	printf "%s\\t%s\\n" "${lineage_id}" "${lineage}" >> metatraits/lineage/${lineage_id}.txt
	"""
}
