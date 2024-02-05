#!/bin/bash

set -e

COMPOSE_FILE_PATH="${COMPOSE_FILE_PATH:-"$GITHUB_ACTION_PATH/compose.yml"}"

# start scenario runner to evaluate scenario
docker compose -f $COMPOSE_FILE_PATH  run --rm carla-scenario-runner
