FROM armbuild/alpine:latest

RUN apk add --update --no-cache \
    python2 \
    portaudio \
    alsa-lib

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

CMD ["python", "/opt/open_ears.py"]

VOLUME out

COPY open_ears.py opt/
