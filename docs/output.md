# Output

`porTraits` produces a main table `collated/portraits_results.tsv.gz` in which the main predictor results are collated. 
If `metatraits` reference queries were enabled (`--query_metatraits both|GTDB|NCBI`), then there will be additional 
output tables (`collated/metatraits_gtdb.tsv.gz` and/or `collated/metatraits_ncbi.tsv.gz`, resp.)

In addition, `porTraits` produces the following outputs per genome, organized into subdirectories by tool and function:

## Directory Structure and Main Output Files

- `gtdb/<genome>/gtdbtk/classify`  
  Contains GTDB-Tk taxonomy assignments.
  - `<genome>.gtdbtk.bac120.summary.tsv` or `<genome>.gtdbtk.ar53.summary.tsv`: GTDB taxonomy summary for bacteria or archaea

- `ncbi/<genome>/recognise`
  Contains reCOGnise taxonomy assignments.
  - `<genome>.cogs.txt`: text file containing the MAPseq results for specI classification
  - `<genome>.specI.status`: text file with the status of the species assignment
  - `<genome>.specI.txt`: species (specI cluster) assignment

- `<genome>/e2m/`  
  Contains KEGG and Pfam annotation matrices.
  - `<genome>.emapper.KEGG_ko.tsv.gz`: KEGG ortholog predictions matrix
  - `<genome>.emapper.PFAMs.tsv.gz`: Pfam domain predictions matrix

- `<genome>/bacdive_ai/`  
  Contains genome-wide BacDive-AI trait predictions.
  - `<genome>.BacDiveAI.binary.tsv.gz`: binarized predictions
  - `<genome>.BacDiveAI.prob.tsv.gz`: prediction probabilities

- `<genome>/micropherret/`  
  Contains genome-wide MICROPHERRET trait predictions.
  - `<genome>.MICROPHERRET.binary.tsv.gz`: binarized predictions
  - `<genome>.MICROPHERRET.prob.tsv.gz`: prediction probabilities
 
- `<genome>/genomeSPOT/`  
  Contains genome-wide genomeSPOT trait predictions.
  - `<genome>.genomeSPOT.binary.tsv.gz`: predictions

- `<genome>/traitar/`  
  Contains genome-wide Traitar trait predictions.
  - `<genome>.Traitar.binary.tsv.gz`: binarized predictions (consensus across SVM models)
  - `<genome>.Traitar.original.tsv.gz`: Original Traitar format [0: absent, 1: phypat, 2: phypat_PGL, 3: both]
  - `<genome>.Traitar.prob.tsv.gz`: prediction probabilities, estimated by applying a sigmoid function to the raw SVM decision scores (distance from the hyperplane)
