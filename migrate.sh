#!/usr/bin/env bash
# Run from repo root, or from anywhere: the script changes to the directory it lives in.
# Requires: docker compose up (stack running) and images built so migrations exist in containers.
set -e
cd "$(dirname "$0")"

docker compose exec listing-service python manage.py migrate
docker compose exec auction-service python manage.py migrate
docker compose exec wallet-service python manage.py migrate
docker compose exec user-service python manage.py migrate
docker compose exec order-service python manage.py migrate
