#!/bin/bash
default_demo="software-prototyping"
selected_demo=""

docker_compose_command="docker compose" # change to docker-compose if old version is used

if [ $# -eq 0 ]; then
  echo "No demo manually selected. Selecting default demo..."
  selected_demo=$default_demo
else
  selected_demo=$1
  if [ ! -f "$selected_demo/docker-compose.yml" ]; then
    echo "No demo called $selected_demo exists. Please check available demos and run again."
    exit 1
  fi
fi

# trap ctrl-c and killing the bash to call cleanup function
trap cleanup EXIT
trap cleanup 0

function cleanup() {
  echo "Cleaning up..."
  $docker_compose_command -f $selected_demo/docker-compose.yml down
  xhost -local:
  echo "Done cleaning up."
}

xhost +local:

echo "Running demo: $selected_demo"

$docker_compose_command -f $selected_demo/docker-compose.yml up 
