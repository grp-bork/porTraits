# porTraits: a metaTraits workflow
<table>
  <tr width="100%">
    <td width="150px">
      <a href="https://www.bork.embl.de/"><img src="https://www.bork.embl.de/assets/img/normal_version.png" alt="Bork Group Logo" width="150px" height="auto"></a>
    </td>
    <td width="425px" align="center">
      <b>Developed by the <a href="https://www.bork.embl.de/">Bork Group</a></b><br>
      Raise an <a href="https://github.com/grp-bork/porTraits/issues">issue</a> or <a href="mailto:N4M@embl.de">contact us</a><br><br>
      See our <a href="https://www.bork.embl.de/services.html">other Software & Services</a>
    </td>
    <td width="500px">
      Contributors:<br>
      <ul>
        <li>
          <a href="https://github.com/cschu/">Christian Schudoma</a> <a href="https://orcid.org/0000-0003-1157-1354"><img src="https://orcid.org/assets/vectors/orcid.logo.icon.svg" alt="ORCID icon" width="20px" height="20px"></a><br>
        </li>
        <li>
          <a href="https://github.com/danielpodlesny/">Daniel Podlesny</a> <a href="https://orcid.org/0000-0002-5685-0915"><img src="https://orcid.org/assets/vectors/orcid.logo.icon.svg" alt="ORCID icon" width="20px" height="20px"></a><br>
        </li>
      </ul>
    </td>
  </tr>
  <tr>
    <td colspan="3" align="center">The development of this workflow was supported by <a href="https://www.nfdi4microbiota.de/">NFDI4Microbiota <img src="https://github.com/user-attachments/assets/1e78f65e-9828-46c0-834c-0ed12ca9d5ed" alt="NFDI4Microbiota icon" width="20px" height="20px"></a> 
</td>
  </tr>
</table>


---
#### Description
`porTraits` is a [metaTraits](https://metaTraits.embl.de/) workflow for annotating microbial phenotypic traits. Developed in Nextflow, `porTraits` integrates multiple genome-based trait prediction tools ([BacDive-AI](https://github.com/LeibnizDSMZ/bacdive-AI/), [GenomeSPOT](https://github.com/cultivarium/GenomeSPOT), [Traitar](https://github.com/hzi-bifo/traitar), [MICROPHERRET](https://github.com/MetabioinfomicsLab/MICROPHERRET/)) to provide comprehensive trait annotations. The workflow also includes NCBI and GTDB taxonomy assignment, and provides context by linking to related trait records within the [metaTraits](https://metaTraits.embl.de/) database. 

#### Citation
This workflow: [![DOI](https://zenodo.org/badge/1015960396.svg)](https://doi.org/10.5281/zenodo.16809306)


Also cite:
```
TBD
```

---
# Overview
`porTraits` takes genome or MAG fasta files as input, calls genes with prodigal, creates KO and PFAM matrices with eggNOG-mapper, and uses the matrices to compute model predictions from [BacDive-AI](https://github.com/LeibnizDSMZ/bacdive-AI/), [Traitar](https://github.com/hzi-bifo/traitar), and [MICROPHERRET](https://github.com/MetabioinfomicsLab/MICROPHERRET/). [GenomeSPOT](https://github.com/cultivarium/GenomeSPOT) is run from scratch. [GTDB-Tk](https://github.com/Ecogenomics/GTDBTk) and [reCOGnise](https://github.com/grp-bork/reCOGnise/) are run to obtain GTDB (r220) and NCBI taxonomy, respectively, which is used to retrieve highly similar trait records from the [metaTraits](https://metaTraits.embl.de/) database for context.


---
# Requirements

`porTraits` requires a docker/singularity installation. All dependencies are contained in the `porTraits` docker container.

## porTraits databases

Obtain databases required to run `porTraits` from Zenodo: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16818976.svg)](https://doi.org/10.5281/zenodo.16818976)

---
# Database

The reCOGnise marker database can be downloaded from [Zenodo](https://zenodo.org/records/17916463/files/recognise_markers.tar.gz).

---
# Usage
## GUI-based Execution (CloWM)
This workflow is available on `CloWM`, the [Cloud-based Workflow Manager](https://clowm.bi.denbi.de/workflows/). `CloWM` enables user-friendly workflow execution in the cloud: no command line or installation required, free for academic use.

## Command-Line Interface (CLI)
The workflow run is controlled by environment-specific parameters (see [run.config](https://github.com/grp-bork/porTraits/blob/main/config/run.config)). The parameters in the `params.yml` can be specified on the command line as well.

You can either clone this repository from GitHub and run it as follows
```
git clone https://github.com/grp-bork/porTraits.git
nextflow run /path/to/porTraits.nf [-resume] -c /path/to/run.config -params-file /path/to/params.yml
```

Or, you can have nextflow pull it from github and run it from the `$HOME/.nextflow` directory.
```
nextflow run grp-bork/porTraits.nf [-resume] -c /path/to/run.config -params-file /path/to/params.yml
```

## Input files
Input genome fasta files have to have one of the following file endings: `{fna,fasta,fa,fna.gz,fasta.gz,fa.gz}`. Alternatively, you can set the pattern with
`params.file_pattern = "**.{<comma-separated-list-of-file-endings>}"`.




