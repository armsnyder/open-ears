FROM armbuild/alpine:latest

CMD ["python", "/opt/open_ears.py"]

RUN apk add --update \
    python2 \
    portaudio

RUN apk add --update \
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

COPY app/* opt/
