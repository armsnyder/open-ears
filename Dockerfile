FROM armhf/alpine:latest

RUN apk add --update --no-cache python2

RUN apk add --update --no-cache py-numpy

RUN apk add --update --no-cache portaudio

RUN apk add --update --no-cache libsndfile

# build and install python scikits.audiolab
RUN apk add --update --no-cache py2-pip py-numpy-dev libsndfile-dev musl-dev && \
    pip install --no-cache-dir scikits.audiolab && \
    apk del py2-pip py-numpy-dev libsndfile-dev musl-dev

# build and install python sounddevice
RUN apk add --update --no-cache py2-pip python2-dev portaudio-dev gcc libc-dev libffi-dev && \
    pip install --no-cache-dir sounddevice && \
    apk del py2-pip python2-dev portaudio-dev gcc libc-dev libffi-dev

CMD ["python", "/opt/open_ears.py"]

VOLUME out

COPY open_ears.py opt/
