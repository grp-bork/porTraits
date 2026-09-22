FROM condaforge/miniforge3:24.7.1-0

LABEL maintainer="cschu1981@gmail.com"
LABEL version="2.2"
LABEL description="This is a Docker image for the porTraits workflow"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y

RUN apt install -y wget python3-pip git
RUN apt clean

# communication "layer"
RUN pip install pandas requests

# Environment with scikit-learn 1.4.0
# traitar / bacdive
RUN conda create -y -n traitar_bacdive \
    python>=3.9 \
    scikit-learn=1.4.0 \
    pandas=2.3.1 \
    && conda clean -afy
 
# Environment with scikit-learn 1.2.2
# micropherret
RUN conda create -y -n micropherret \
    python=3.9 \
    scikit-learn=1.2.2 \
    pandas \
    biopython \
    numpy \
    tensorflow \
    && /opt/conda/envs/micropherret/bin/python -m pip install \
        --no-cache-dir \
        tensorflow-addons \
    && conda clean -afy

# Environment with scikit-learn 1.2.2
# genomespot
WORKDIR /opt/software

RUN git clone https://github.com/cultivarium/GenomeSPOT.git genomespot \
    && cd genomespot \
    && git checkout b6102dc350216ceb9e451a5ccd6dc3b412d04f4e \
    && touch genome_spot/bioinformatics/hmm/__init__.py \
    && sed -i '36i\ \ \ \ entry_points={"console_scripts": \["genomespot=genome_spot.genome_spot:main",\]},' setup.py \
    && conda create -y -n genomespot \
        "python>=3.9,<3.12" \
        scikit-learn=1.2.2 \
        pandas>=1.5.3 \
        biopython \
        numpy>=1.23.5 \
        bacdive>=0.2 \
        hmmlearn=0.3.0 \
    && /opt/conda/envs/genomespot/bin/python -m pip install . \
    && /opt/conda/envs/genomespot/bin/python -m pip install -r requirements.txt \
    && conda clean -afy \
    && printf '#!/bin/sh\nexec /opt/conda/envs/genomespot/bin/python "$@"\n' \
        > /usr/local/bin/python_gs \ 
    && chmod +x /usr/local/bin/python_gs
