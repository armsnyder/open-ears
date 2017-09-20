# Open Ears
[![Build Status](https://semaphoreci.com/api/v1/armsnyder/open-ears/branches/master/badge.svg)](https://semaphoreci.com/armsnyder/open-ears)

## The Problem

I have a parrot named Greg who has recently started making a very specific, very load, 
high-pitched beep. When I am close enough to her cage, the sound is loud enough to cause real ear
damage.

## The Solution

Open Ears is a Dockerized Python script which runs on a Raspberry Pi with a microphone. It 
constantly monitors the sound near Greg's cage for the very specific beep that is a problem. When
it detects the beep, it triggers a mild negative stimulus: it flashes a ceiling lamp near the cage.

Disclaimer: Parrot training works best with rewarding positive behavior and ignoring negative
behavior. Open Ears is meant to supplement these methods and is very experimental.

## Details

Open Ears runs several processes using the `multiprocessing` module. The processes that monitor the
microphone input stream are layered in complexity such that the cheap processes like calculating 
the volume are run before the more expensive processes like fourier transforms.

## Deployment

Open Ears can be built and deployed as a Docker image. The reason for using Docker is to separate
the hairy system-level audio libraries from the base Raspberry Pi filesystem.

Since it is intended to be deployed to the ARM-based Raspberry Pi, but built on x86-based machines, 
the Docker image is built on top of the resin/armv7hf-debian-qemu image.

Continuous deployment is enabled on this repository, so pushes to `master` trigger automated
build and deployment directly to the Raspberry Pi under Greg's cage.

Note that in order for microphones to be available inside the Docker container they must be bound.

Example:
```bash
$ docker build . -t openears
$ docker run -d --restart always --device /dev/snd -v /home/pi/out:/out openears
```
