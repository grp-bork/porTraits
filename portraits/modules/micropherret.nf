process micropherret {
	tag "${genome_id}"
	label "tiny"

	input:
	tuple val(genome_id), path(ko_matrix)
	path(micropherret_models)

	output:
	tuple val(genome_id), path("${genome_id}/micropherret/*.MICROPHERRET.*.tsv.gz"), emit: predictions

	script:
	"""
	mkdir -p ${genome_id}/micropherret/
	KO2MICROPHERRET.py --ko-matrix ${ko_matrix} --model-dir ${micropherret_models} --outdir ${genome_id}/micropherret &> warnings.txt || :

	if [[ ! -f ${genome_id}/micropherret/MICROPHERRET.prob.tsv.gz ]]; then
	  touch warnings.txt
	  gzip -c warnings.txt > ${genome_id}/micropherret/MICROPHERRET.prob.tsv.gz
	fi

	find ${genome_id}/ -type f | xargs -I{} sh -c 'mv {} \$(dirname {})/${genome_id}.\$(basename {})'
	"""
}