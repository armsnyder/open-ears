FROM armbuild/alpine:latest

CMD ["python", "/opt/open_ears.py"]

RUN apk add --update \
  python2 \
  py2-pip

COPY app/requirements.txt opt/
RUN pip install -r /opt/requirements.txt

COPY app/* opt/
