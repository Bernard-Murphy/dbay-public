#!/usr/bin/env bash
#
# Tear down the entire app and purge all containers, volumes, networks,
# and project-built images so the repo is left as if freshly cloned.
# Run from repo root, or from anywhere (script changes to its directory).
#
set -e
cd "$(dirname "$0")"

echo "==> Stopping and removing containers, networks, volumes, and project-built images..."
docker compose down -v --rmi local

echo "==> Done. No containers, volumes, or project images remain. Run ./local.sh or docker compose up -d --build to start again."
