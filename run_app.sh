#!/bin/bash
image="blustoryframeconv"

newv=$(head -c 32 /dev/urandom | sha256sum | cut -d' ' -f1)


export FULL_IMAGE=palondomus/$image:$newv
export IMAGE=$image
export NEWV=$newv

# Push Docker
docker compose -f docker-compose.local.yml build 

docker compose -f docker-compose.local.yml up














