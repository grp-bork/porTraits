VERSION 0.2.3

- changed all internal dependency containers to github-hosted
- adjusted scripts/process blocks to new container

VERSION 0.2.2 (housekeeping)

- added Dockerfile / docker-publish action
  this container hosts genomespot, environments for micropherret, bacdive-ai, traitar
  as well as for the metatraits communication and collate processes

VERSION 0.2.1

- updated recognise to v0.8.0 and adjusted call in recognise.nf
- updated genomespot container to reflect proper version (genomespot-docker:v1.0.1plus)

VERSION v0.2.0

- fixed NCBI-based metatraits reference queries
- fixed output bug in PFAM2Traitar
- made gtdbtk --mash_db parameter optional (internally)
- process outputs are now prefixed with genome id
- cleaned up and limited outputs
- added metatraits gtdb queries
- added result collation (added reference data files to repo)
- added toggle for metatraits reference queries
- cosmetics
- updated documentation