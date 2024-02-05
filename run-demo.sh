#!/bin/bash
default_demo="software-prototyping"
selected_demo=""

docker_compose_command="docker compose" # change to docker-compose if old version is used

if [ $# -eq 0 ]; then
  echo "No demo manually selected. Selecting default demo..."
  selected_demo=$default_demo
else
  selected_demo=$1
fi

if [ "$selected_demo" != "data-driven-development" ] && [ "$selected_demo" != "automated-testing" ] && [ ! -f "$selected_demo/docker-compose.yml" ]; then
  echo "No demo called $selected_demo exists. Please check available demos and run again."
  exit 1
fi

# trap ctrl-c and killing the bash to call cleanup function
trap cleanup EXIT
trap cleanup 0

function cleanup() {
  echo "Cleaning up..."
  if [ "$selected_demo" != "data-driven-development" ] && [ "$selected_demo" != "automated-testing" ]; then
    $docker_compose_command -f $selected_demo/docker-compose.yml down
  fi
  xhost -local:
  echo "Done cleaning up."
}

xhost +local:

echo "Running demo: $selected_demo"

if [ "$selected_demo" = "data-driven-development" ]; then
  env_name=$(grep 'name:' $selected_demo/env/environment.yml | awk '{print $2}')
  conda_bin_dir=$(dirname $(which conda))
  conda env list | grep "^${env_name} " > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Conda environment '$env_name' does not exist. Creating it..."
    conda env create -f $selected_demo/env/environment.yml
  fi
  source $conda_bin_dir/activate $env_name
  cd $selected_demo
  python data_generation.py
elif [ "$selected_demo" = "automated-testing" ]; then
  cd $selected_demo
  ./evaluate-scenarios.sh
else
  $docker_compose_command -f $selected_demo/docker-compose.yml up
fi
