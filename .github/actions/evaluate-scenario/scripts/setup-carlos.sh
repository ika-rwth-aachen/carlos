#!/bin/bash

set -e

COMPOSE_FILE_PATH="${COMPOSE_FILE_PATH:-"$GITHUB_ACTION_PATH/compose.yml"}"
COMPOSE_TEMPLATE_PATH="${COMPOSE_TEMPLATE_PATH:-"$GITHUB_ACTION_PATH/files/template.yml"}"

if [ "$SIMULATOR_OFFSCREEN" = true ]; then
  export SIMULATOR_FLAGS="-RenderOffScreen"
fi

# generate compose file from template and environment variables
if [ ! -f $COMPOSE_FILE_PATH ]; then
  (envsubst < $COMPOSE_TEMPLATE_PATH) > $COMPOSE_FILE_PATH
fi

# provide full compose file as output
echo "compose-file<<EOF" >> $GITHUB_OUTPUT
echo "$(cat $COMPOSE_FILE_PATH)" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT

# start simulator
xhost +local:
docker compose -f $COMPOSE_FILE_PATH  up -d carla-simulator
