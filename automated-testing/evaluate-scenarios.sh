#!/bin/bash

set -e

usage() {
  echo "Usage: $0 [-d maxdepth] [-e exclude-path] STARTING-POINT QUERY-STRING"
  echo "STARTING-POINT : Location from where search should start"
  echo "QUERY-STRING : UNIX pattern used for matching and selecting results. Needs to be \"quoted\""
  echo "max-depth : Descend at most max-depth levels from STARTING-POINT"
  echo "exclude-string : Exclude paths matching this UNIX pattern from final result. Needs to be \"quoted\""
  echo "-----"
  echo "Example: $0 -d 3 . \"*.xosc\""
}

trap cleanup EXIT
trap cleanup 0

cleanup() {
  echo "Cleaning up..."
  docker compose -f $COMPOSE_TEMPLATE_PATH kill
  docker compose -f $COMPOSE_TEMPLATE_PATH down
  xhost -local:
  echo "Done cleaning up."
}

restart-simulator() {
  echo "Restarting simulator..."
  docker compose -f $COMPOSE_TEMPLATE_PATH kill
  docker compose -f $COMPOSE_TEMPLATE_PATH down
  docker compose -f $COMPOSE_TEMPLATE_PATH up -d carla-simulator
}

export SCENARIO_DIRECTORY="${1:-"../utils/scenarios"}"
export COMPOSE_TEMPLATE_PATH="${2:-"./template.yml"}"
echo $SCENARIO_DIRECTORY

scenarios=($(find $SCENARIO_DIRECTORY -maxdepth 1 -type f -name "*.xosc*" -exec basename {} \;))

if [ ${#scenarios[@]} -eq 0 ]; then
  echo "No scenarios found. Exiting..."
  exit 1
fi
xhost +local:
echo "Starting simulator..."
docker compose -f $COMPOSE_TEMPLATE_PATH up -d carla-simulator

for scenario in "${scenarios[@]}"; do
  echo "Evaluating $scenario ..."

  export SCENARIO_NAME=$scenario 
  docker compose -f $COMPOSE_TEMPLATE_PATH  run --rm carla-scenario-runner || true

  if [ "$RESTART_SIMULATOR" = true ]; then
    restart-simulator
  fi
done
