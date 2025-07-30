process micropherret {
	tag "${genome_id}"

	input:
	tuple val(genome_id), path(ko_matrix)
	path(micropherret_models)

	output:
	tuple val(genome_id), path("${genome_id}/micropherret/**.tsv.gz"), emit: predictions

	script:
	"""
	mkdir -p ${genome_id}/micropherret/
	KO2MICROPHERRET.py --ko-matrix ${ko_matrix} --model-dir ${micropherret_models} --outdir ${genome_id}/micropherret
	"""
}