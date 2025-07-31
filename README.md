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
`porTraits` is a [metaTraits](https://metaTraits.embl.de/) workflow for microbial phenotypic trait annotation. Written in Nextflow, the `porTraits` workflow computes genome-based trait predictions from multiple trait annotation tools ([BacDive-AI](https://github.com/LeibnizDSMZ/bacdive-AI/), [GenomeSPOT](https://github.com/cultivarium/GenomeSPOT), [Traitar](https://github.com/hzi-bifo/traitar), [MICROPHERRET](https://github.com/MetabioinfomicsLab/MICROPHERRET/)), along with NCBI and GTDB taxonomy prediction and linking to relevant reference genomes in the [metaTraits](https://metaTraits.embl.de/) database. 


#### Citation
This workflow: [![DOI](tbd)](tbd)

Also cite:
```
TBD
```

---
# Overview
tbd

---
# Requirements

`porTraits` requires a docker/singularity installation. All dependencies are contained in the `porTraits` docker container.


## porTraits databases

Obtain databases required to run `porTraits` from Zenodo: TBD

---
# Usage
## Cloud-based Workflow Manager (CloWM)
This workflow is available on the `CloWM` platform (https://clowm.bi.denbi.de/workflows/).

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
