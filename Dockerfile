FROM armhf/debian:latest

RUN apt-get update && \
    apt-get install -y \
    python-numpy \
    python-scipy \
    libportaudio2 \
    python-cffi

RUN apt-get update && \
    apt-get install -y \
    python-pip \
    python-dev \
    portaudio19-dev \
    libffi-dev \
    wget && \
    pip install sounddevice && \
    mkdir -p /opt/lib && \
    wget -O /opt/lib/iso226.py https://raw.githubusercontent.com/jcarrano/rtfi/master/iso226.py && \
    apt-get remove -y \
    python-pip \
    python-dev \
    portaudio19-dev \
    libffi-dev \
    wget && \
    apt-get autoremove -y

CMD ["python", "/opt/open_ears.py"]

VOLUME out

COPY open_ears.py opt/

COPY lib/ opt/lib/
