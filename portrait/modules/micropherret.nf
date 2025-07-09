process micropherret {
	tag "${genome_id}"

	input:
	tuple val(genome_id), path(ko_matrix)
	path(micropherret_models)

	script:
	"""
	mkdir -p micropherret/${genome_id}/
	KO2MICROPHERRET.py --ko-matrix ${ko_matrix} --model-dir ${micropherret_models} --outdir micropherret/${genome_id}
	"""
}