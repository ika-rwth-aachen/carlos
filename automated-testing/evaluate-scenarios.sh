#!/bin/bash

set -e

DEFAULT_SIMULATOR_IMAGE="rwthika/carla-simulator:server"
DEFAULT_SCENARIO_RUNNER_IMAGE="rwthika/carla-scenario-runner:latest"
COMPOSE_TEMPLATE_PATH="./template.yml"

usage() {
  echo "Usage: $0 [-o][-p][-n] [COMPOSE_TEMPLATE_PATH] [SCENARIO_FOLDER_PATH]"
  echo "COMPOSE_TEMPLATE_PATH : Location of Compose file which can be customized through environment variables"
  echo "SCENARIO_FOLDER_PATH : Location of folder containing scenario files ending with .xosc*"
  echo "o : Set the simulator to offscreen mode"
  echo "p : Pull/Update images before starting the simulation"
  echo "n : Do not restart the simulator after each scenario run"
  echo "-----"
  echo "Environment variables for customization:"
  echo "SIMULATOR_IMAGE : CARLA image that should be used"
  echo "SCENARIO_RUNNER_IMAGE : CARLA Scenario Runner image that should be used"
  echo "TIME_BETWEEN_EVALS" : Delay between each scenario run in seconds
  echo "-----"
  echo "Example:"
  echo "SIMULATOR_IMAGE=rwthika/carla:dev $0 -r ./template.yml ./scenarios"
}

restart-simulator() {
  echo "Restarting simulator..."
  docker compose -f $COMPOSE_TEMPLATE_PATH kill
  docker compose -f $COMPOSE_TEMPLATE_PATH down
  docker compose -f $COMPOSE_TEMPLATE_PATH up -d carla-server
}

update-simulator() {
  echo "Updating simulator..."
  docker compose -f $COMPOSE_TEMPLATE_PATH pull
}

while getopts "hopn" flag; do
case "$flag" in
  h) 
    usage
    exit 0
    ;;
  o) 
    export SIMULATOR_OFFSCREEN=true
    ;;
  p) 
    update-simulator
    ;;
  n) 
    export RESTART_SIMULATOR=false
    ;;
esac
done

shift $(($OPTIND-1)) # return to usual handling of positional args

# default settings if no external overrides provided
export SIMULATOR_IMAGE=${SIMULATOR_IMAGE:-DEFAULT_SIMULATOR_IMAGE}
export SCENARIO_RUNNER_IMAGE=${SCENARIO_RUNNER_IMAGE:-DEFAULT_SCENARIO_RUNNER_IMAGE}

export COMPOSE_TEMPLATE_PATH=$(realpath ${1:-$COMPOSE_TEMPLATE_PATH})
export SCENARIO_FOLDER_PATH=$(realpath ${2:-"../utils/scenarios"})

export RESTART_SIMULATOR=${RESTART_SIMULATOR:-true}
export TIME_BETWEEN_EVALS=${TIME_BETWEEN_EVALS:-5}

export SIMULATOR_FLAGS=""
export SCENARIO_FILE_NAME=""

trap cleanup EXIT
trap cleanup 0

cleanup() {
  echo "Cleaning up..."
  RESTART_SIMULATOR=false
  docker compose -f $COMPOSE_TEMPLATE_PATH kill
  docker compose -f $COMPOSE_TEMPLATE_PATH down
  xhost -local:
  echo "Done cleaning up."
  exit
}

echo "Searching for scenarios in $SCENARIO_FOLDER_PATH  ..."
scenarios=($(find $SCENARIO_FOLDER_PATH -maxdepth 1 -type f -name "*.xosc*" -exec basename {} \;))

if [ ${#scenarios[@]} -eq 0 ]; then
  echo "No scenarios found. Exiting..."
  exit 1
fi

if [ "$SIMULATOR_OFFSCREEN" = true ]; then
  export SIMULATOR_FLAGS="-RenderOffScreen"
fi

xhost +local:
echo "Starting simulator..."
docker compose -f $COMPOSE_TEMPLATE_PATH up -d carla-server

for scenario in "${scenarios[@]}"; do
  echo "Evaluating $scenario ..."
  export SCENARIO_FILE_NAME=$scenario 
  
  docker compose -f $COMPOSE_TEMPLATE_PATH  run --rm carla-scenario-runner || true

  if [ "$RESTART_SIMULATOR" = true ]; then
    restart-simulator
  fi

  sleep $TIME_BETWEEN_EVALS
done
