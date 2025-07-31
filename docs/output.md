# Output

`porTraits` produces the following outputs, organized into subdirectories by tool and function:

## Directory Structure and Main Output Files

- `gtdb/`  
  Contains GTDB-Tk taxonomy assignments.
  - `gtdbtk.bac120.summary.tsv` or `gtdbtk.ar53.summary.tsv`: GTDB taxonomy summary for bacteria or archaea

- `ncbi/`
  Contains reCOGnise taxonomy assignments.
  - `<sample>.specI.status.OK`: text file signifying if species assignment was successful
  - `<sample>.specI.status`: text file with the status of the species assignment
  - `<sample>.specI.txt`" species (specI cluster) assignment

- `e2m/`  
  Contains KEGG and Pfam annotation matrices.
  - `emapper.KEGG_ko.tsv.gz`: KEGG ortholog predictions matrix
  - `emapper.PFAMs.tsv.gz`: Pfam domain predictions matrix

- `bacdive_ai/`  
  Contains genome-wide BacDive-AI trait predictions.
  - `BacDiveAI.binary.tsv.gz`: binarized predictions
  - `BacDiveAI.prob.tsv.gz`: prediction probabilities

- `micropherret/`  
  Contains genome-wide MICROPHERRET trait predictions.
  - `MICROPHERRET.binary.tsv.gz`: binarized predictions
  - `MICROPHERRET.prob.tsv.gz`: prediction probabilities
 
- `genomeSPOT/`  
  Contains genome-wide genomeSPOT trait predictions.
  - `genomeSPOT.binary.tsv.gz`: predictions

- `traitar/`  
  Contains genome-wide Traitar trait predictions.
  - `Traitar.binary.tsv.gz`: binarized predictions (consensus across SVM models)
  - `Traitar.original.tsv.gz`: Original Traitar format [0: absent, 1: phypat, 2: phypat_PGL, 3: both]
  - `Traitar.prob.tsv.gz`: prediction probabilities, estimated by applying a sigmoid function to the raw SVM decision scores (distance from the hyperplane)
