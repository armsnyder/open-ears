FROM armbuild/alpine:latest

# install system dependencies
RUN apk add --update --no-cache \
    python2 \
    portaudio \
    alsa-lib

# install python dependencies with pip
RUN apk add --update --no-cache \
    python2-dev \
    py2-pip \
    portaudio-dev \
    gcc \
    libc-dev && \
    pip install pyaudio wave && \
    apk del \
    python2-dev \
    py2-pip \
    portaudio-dev \
    gcc \
    libc-dev

# delete unknown devices configured by default in alsa-lib
RUN sed -i 132,148d /usr/share/alsa/alsa.conf

CMD ["python", "/opt/open_ears.py"]

VOLUME out

COPY open_ears.py opt/
