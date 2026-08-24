#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  echo "ERROR: .env file was not found."
  exit 1
fi

docker compose up -d --build --remove-orphans
docker compose ps
