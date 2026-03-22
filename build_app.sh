#!/usr/bin/env bash

set -e

MODE="$1"

if [[ -z "$MODE" ]]; then
  echo "Usage: ./build_app.sh --local | --prod"
  exit 1
fi
artifact_repo="palondomus"
image="blustoryapi"

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
  --test)
   echo "🔧 Running Tests..."

    # Clean start
    docker compose -f docker-compose.local.yml down -v

    # Start DB
    docker compose -f docker-compose.local.yml up -d postgres

    # Wait for DB
    until docker compose -f docker-compose.local.yml exec postgres pg_isready; do
      echo "Waiting for postgres..."
      sleep 1
    done

    # Run migrations
    docker compose -f docker-compose.local.yml build migrate && docker compose -f docker-compose.local.yml run --rm -e ENVIRONMENT=test migrate

    # Run tests
    docker compose -f docker-compose.local.yml build test && docker compose -f docker-compose.local.yml run --rm test

    # Cleanup
    docker compose -f docker-compose.local.yml down -v
   #
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