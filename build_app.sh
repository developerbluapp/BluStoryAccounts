#!/bin/bash
artifact_repo="palondomus"
image="blustoryframeconv"

newv=$(head -c 32 /dev/urandom | sha256sum | cut -d' ' -f1)

# Auth GCP Cloud
gcloud auth application-default login


export FULL_IMAGE="$artifact_repo/$image:$newv"
export IMAGE=$image
export NEWV=$newv

# Push Docker
docker compose build
docker push $artifact_repo/$image:$newv


export TF_VAR_image="$artifact_repo/$image:$newv"
cd deployment
# Terraform Push Google Cloud
terraform init
terraform plan 
terraform apply -auto-approve
cd ..
# Push Github
git add .
git commit -m "$1"
git push origin -u main:main

docker compose up














