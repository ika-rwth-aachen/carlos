#!/bin/bash

set -e

COMPOSE_FILE_PATH="${COMPOSE_FILE_PATH:-"$GITHUB_ACTION_PATH/compose.yml"}"

# kill and remove remaining CARLOS setup
docker compose -f $COMPOSE_FILE_PATH kill
docker compose -f $COMPOSE_FILE_PATH down
