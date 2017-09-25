FROM resin/armv7hf-debian-qemu:latest

ENV PATH=/miniconda/bin:${PATH}

RUN ["cross-build-start"]

# Install conda
RUN apt-get update && \
    apt-get install -y \
    curl \
    bzip2 \
    libportaudio2 && \
    curl -LO https://repo.continuum.io/miniconda/Miniconda-latest-Linux-armv7l.sh && \
    bash Miniconda-latest-Linux-armv7l.sh -p /miniconda -b && \
    rm Miniconda-latest-Linux-armv7l.sh

# Install conda packages
RUN conda update -y conda && \
    conda install -y numpy scipy scikit-learn && \
    conda install -y -c seibert llvmlite

# Install python pip packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    portaudio19-dev \
    libffi-dev && \
    pip install \
    sounddevice \
    numpy_ringbuffer \
    librosa \
    phue && \
    apt-get remove -y \
    build-essential \
    portaudio19-dev \
    libffi-dev && \
    apt-get autoremove -y

RUN ["cross-build-end"]

CMD ["python", "/opt/open_ears.py"]

COPY secrets/.python_hue root/

COPY src/ opt/
