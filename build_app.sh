#!/usr/bin/env bash

set -e

MODE="$1"

if [[ -z "$MODE" ]]; then
  echo "Usage: ./build_app.sh --local | --prod"
  exit 1
fi
artifact_repo="palondomus"
image="blustorylicenseholders"

newv=$(head -c 32 /dev/urandom | sha256sum | cut -d' ' -f1)
export FULL_IMAGE="$artifact_repo/$image:$newv"
export IMAGE=$image
export NEWV=$newv

case "$MODE" in
  --migrate)
    echo "🔧 Running database migrations..."
    docker compose -f docker-compose.local.yml build migrate && docker compose -f docker-compose.local.yml run --rm migrate
    ;;
  --local)
    echo "🔧 Building LOCAL environment..."
    docker compose -f docker-compose.local.yml build web \
      --build-arg DOCKERFILE=Dockerfile.local

    docker compose -f docker-compose.local.yml up web
    ;;

  --prod)
    echo "🚀 Building PRODUCTION environment..."

    # Auth GCP Cloud
    gcloud auth application-default login




    # Push Docker
    docker compose build
    docker push $artifact_repo/$image:$newv


    export TF_VAR_image="$artifact_repo/$image:$newv"
    cd infra
    # Terraform Push Google Cloud
    terraform init
    terraform plan
    terraform apply -auto-approve
    cd ..
    # Push Github
    if [[ "$2" == "--commit" && -n "$3" ]]; then
      msg="$3"
      git add .
      git commit -m "$msg"
      git push origin -u main:main
    fi
    docker compose -f docker-compose.yml build \
      --build-arg DOCKERFILE=Dockerfile

    docker compose -f docker-compose.yml up
    ;;

  *)
    echo "❌ Unknown option: $MODE"
    echo "Use --local or --prod"
    exit 1
    ;;
esac