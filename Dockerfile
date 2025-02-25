

FROM ubuntu:22.04

#Install system dependencies
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y \
    openjdk-17-jre-headless \
    python3 \
    python3-pip \
    build-essential \
    curl \
    emboss \
    git \
    wget \
    bzip2

#Install nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

#Install foldseek
RUN mkdir -p /tmp/foldseek && \
    cd /tmp/foldseek && \
    wget https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz && \
    tar xvzf foldseek-linux-avx2.tar.gz && \
    mv foldseek /usr/local/bin/ && \
    rm -rf /tmp/foldseek


RUN rm -rf /var/lib/apt/lists/*

#Clone github repo
RUN git clone https://github.com/zhenou1/mmdp.git && \
    cd /mmdp

#Install python dependencies
RUN pip3 install \
            numpy \
            pandas \
            matplotlib \
            biopython

#Create working directory
WORKDIR /workflow

COPY . /workflow

#Verify installations
RUN nextflow -version && \
    foldseek version && \
    needleall -h

#Set nextflow entrypoint
ENTRYPOINT [ "nextflow" ]