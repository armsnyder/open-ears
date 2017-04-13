# Open Ears
Open Ears is a small Python application that continuously records microphone input, built to run 
on a Raspberry Pi. It exposes a web handler that can be called to save the audio buffer to a file.

This is useful for cases where you have a parrot who occasionally makes shrieking noises and you
need to collect audio samples for another project.

## Local Development

Open Ears uses the PyAudio Python package to record audio, so install that first.

Run the `app/open_ears.py` script to run Open Ears.

## Deployment

Open Ears can be built and deployed as a Docker image. Since it is intended to be deployed to the 
ARM-based Raspberry Pi, the Docker image is built on top of the armbuild/alpine image.

Note that in order for microphones to be available they must be bound to the container.

Example:
```bash
docker build . -t openears
docker run -d --restart always -p 8080:8080 --device /dev/snd -v /home/pi/out:/out openears
```

Why Docker? Mostly to encapsulate the hairy system-level audio dependencies.
