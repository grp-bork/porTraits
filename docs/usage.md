# Usage

## Input
* `input_genomes`: A directory of input genomes. Supported formats are `fna,fasta,fa,fna.gz,fasta.gz,fa.gz`.

## Output
* `outdir`: Path to an output directory where the results are written

## Parameters
* `--query_metatraits`: This can be set to `none`, `both`, `NCBI`, or `GTDB`. Any option other than `none` will make `porTraits` query reference data from `metaTraits` based on the results of the `reCOGnise` (specI -> NCBI) and/or `gtdbtk` (GTDB) taxonomic classification steps.