FROM armhf/debian:latest

# Install python
RUN apt-get update && \
    apt-get install -y \
    python-numpy \
    python-scipy \
    libportaudio2 \
    python-cffi

# Install python pip packages
RUN apt-get update && \
    apt-get install -y \
    python-pip \
    python-dev \
    portaudio19-dev \
    libffi-dev && \
    pip install \
    sounddevice \
    numpy_ringbuffer \
    phue && \
    apt-get remove -y \
    python-pip \
    python-dev \
    portaudio19-dev \
    libffi-dev && \
    apt-get autoremove -y

CMD ["python", "/opt/open_ears.py"]

COPY src/ opt/
