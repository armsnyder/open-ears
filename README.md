# Open Ears

Open Ears is an automated pet trainer.

## The Problem

I have a parrot named Greg who I love very much. We hang out all the time, and even on occasion I 
bring her to work with me. Recently, however, she has started making a very specific, very load, 
high-pitched beep. When I am close enough to her cage, the sound is loud enough to cause real ear
damage.

## The Solution

Open Ears is a Dockerized Python script which runs on a Raspberry Pi with a microphone. It 
constantly monitors the sound near Greg's cage for the very specific beep that is a problem. When
it detects the beep, it triggers a mild negative stimulus: it flashes a ceiling lamp near the cage.

## Details

Open Ears runs several processes using the `multiprocessing` module. The processes that monitor the
microphone input stream are layered in complexity such that the cheap processes like calculating 
the volume are run before the more expensive processes like fourier transforms.

## Deployment

Open Ears can be built and deployed as a Docker image. Since it is intended to be deployed to the 
ARM-based Raspberry Pi, the Docker image is built on top of the armhf/debian image.

Note that in order for microphones to be available they must be bound to the container.

Example:
```bash
$ docker build . -t openears
$ docker run -d --restart always -p 8080:8080 --device /dev/snd -v /home/pi/out:/out openears
```

Why Docker? Mostly to encapsulate the hairy system-level audio dependencies.
