process publish_tarball {
	publishDir path: "${params.output_dir}", mode: "copy"
	label "tiny"
	tag "Publishing results..."

	input:
	path("portraits_results/*")
	val(tarball_prefix)

	output:
	path("*.tar.gz")

	script:
	"""
	touch ${tarball_prefix}.tar.gz
	"""

	// def tarball_prefix = (as_tarball && as_tarball?.trim()) ? "${as_tarball}" : "promgeflow_results"
	// """
	// mkdir -p ${tarball_prefix}/

	// for f in \$(find promgeflow_results_raw -name '*.gff3'); do
	// 	s=\$(basename \$f | sed "s/\\.\\(mge_islands\\|predicted_recombinase_mges\\)\\.gff3//");
	// 	mkdir -p ${tarball_prefix}/\$s;
	// 	find promgeflow_results_raw -name "\$s*" -exec ln -sf ../../{} ${tarball_prefix}/\$s \\;
	// done

	// find promgeflow_results_raw -name '*.txt' -exec ln -sf ../{} ${tarball_prefix}/ \\;

	// find ${tarball_prefix} -name '*.fna.???' | xargs -I{} sh -c 't=\$(ls {} | sed "s/\\.fna\\.\\(faa\\|ffn\\|gff\\)/.\\1/"); mv -v {} \$t;'

	// tar chvzf ${tarball_prefix}.tar.gz ${tarball_prefix}/ 
	// """
		
}
