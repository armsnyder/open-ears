FROM resin/armv7hf-debian-qemu:latest

ENV PATH=/miniconda/bin:${PATH}

RUN ["cross-build-start"]

# system dependencies (for anaconda and sounddevice)
RUN apt-get update && \
    apt-get install -y \
    curl \
    bzip2 \
    libportaudio2

# anaconda (required to get librosa installed alongside everything else)
RUN curl -LO https://repo.continuum.io/miniconda/Miniconda-latest-Linux-armv7l.sh && \
    bash Miniconda-latest-Linux-armv7l.sh -p /miniconda -b && \
    rm Miniconda-latest-Linux-armv7l.sh && \
    conda update -y conda

# conda packages (note: poppy-project provides some needed armv7 distributions)
RUN conda update -y conda && \
    conda install -y \
    numpy \
    scipy \
    scikit-learn && \
    conda install -y -c poppy-project \
    librosa \
    sounddevice

# pip packages not available through conda
RUN pip install \
    numpy_ringbuffer \
    phue

RUN ["cross-build-end"]

CMD ["python", "/opt/open_ears.py"]

COPY secrets/.python_hue root/

COPY src/ opt/
