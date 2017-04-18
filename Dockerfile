FROM armhf/debian:latest

RUN apt-get update && \
    apt-get install -y python-numpy

RUN apt-get update && \
    apt-get install -y libportaudio2

RUN apt-get update && \
    apt-get install -y python-cffi

RUN apt-get update && \
    apt-get install -y python-setuptools

RUN apt-get update && \
    apt-get install -y python-pip python-dev libsndfile-dev libasound2-dev && \
    pip install scikits.audiolab && \
    apt-get remove -y python-pip python-dev libsndfile-dev libasound2-dev && \
    apt-get autoremove -y

RUN apt-get update && \
    apt-get install -y python-pip python-dev portaudio19-dev libffi-dev && \
    pip install sounddevice && \
    apt-get remove -y python-pip python-dev portaudio19-dev libffi-dev && \
    apt-get autoremove -y

CMD ["python", "/opt/open_ears.py"]

VOLUME out

COPY *.py opt/
