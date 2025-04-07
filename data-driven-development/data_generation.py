#!/usr/bin/env python3

import argparse
from ast import List
import itertools
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml
from python_on_whales import DockerClient, DockerException

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        metavar='C',
        default='./config/data-driven-development-demo-image-segmentation.yml',
        help=('Config file which should be used (default:'
              './config/data-driven-development-demo-image-segmentation.yml)'))
    args = parser.parse_args()
    return args


def load_config(
        config_file_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        with config_file_path.open() as config_file:
            config = yaml.safe_load(config_file)
        return config["general_settings"], config["run_settings"]
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_file_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error reading YAML file: {e}")
        sys.exit(1)
    except KeyError as e:
        logging.error(f"The {e} key is missing in the config file")
        sys.exit(1)


def prepare_general_settings(
    general_settings: dict[str, Any]
) -> tuple[dict[str, Any], list[str], list[str]]:
    # Convert required settings to CLI arguments
    cli_args = ["max_real_time", "max_simulation_time"]
    for key in cli_args:
        if key in general_settings:
            general_settings[key] = f"--{key} {general_settings[key]}"
    # Set default output path if required
    if "output_path" not in general_settings:
        general_settings["output_path"] = "./data/"
    if "record_topics" in general_settings:
        output_path = general_settings["output_path"]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Flatten all topics into a single argument
        general_settings["record_topics"] = " ".join(
            general_settings["record_topics"].values())
    # Separate simulation and convert services as they are required somewhere else
    simulation_services = general_settings.pop("simulation_services", None)
    convert_services = general_settings.pop("convert_services", None)
    return general_settings, simulation_services, convert_services


def prepare_permutation(permutation: dict[str, Any]) -> str:
    # Store all left over values of the permutation in a single argument for the simulation controller
    controller_args = []
    for key in list(permutation.keys()):
        if key == "sensors_config_files":
            continue
        if key == "town":
            # Add to controller_args but leave it in the dictionary.
            controller_args.append(f"--{key} {permutation[key]}")
        else:
            value = permutation.pop(key)
            controller_args.append(f"--{key} {value}")
    controller_args_string = " ".join(controller_args)
    permutation["controller_args"] = controller_args_string
    return permutation


def setup_docker_client(docker_compose_file: Path = Path(
    './docker-compose.yml')) -> DockerClient:
    if not docker_compose_file.exists():
        logging.error(f"Docker Compose file not found: {docker_compose_file}")
        sys.exit(1)
    return DockerClient(compose_files=[docker_compose_file])


def validate_sensors_config_files(
        sensors_config_files: list[str]) -> list[str]:
    if not sensors_config_files:
        logging.error("No sensors configuration file specified")
        sys.exit(1)
    sensors_config_files = [
        str(file) for file in map(Path, sensors_config_files)
        if file.is_file() and file.suffix == ".json"
    ]
    return sensors_config_files


def get_role_names(sensor_config_file: str) -> str:
    # The existence of the file is already checked in validate_sensors_config_files
    try:
        with open(sensor_config_file) as file:
            data = json.load(file)
        role_names = [actor["id"] for actor in data["objects"] if actor["type"].startswith("vehicle.")]
        role_names = " ".join(role_names)
        return role_names
    except json.JSONDecodeError as e:
        logging.error(f"Error reading JSON file: {e}")
        sys.exit(1)

def simulate_single_permutation(docker_client: DockerClient,
                                general_settings: dict[Any],
                                permutation: dict[Any],
                                simulation_services: list[str]) -> None:
    run_name = '_'.join([str(value) for value in permutation.values()])
    permutation = prepare_permutation(permutation)
    role_names = get_role_names(permutation["sensors_config_files"])
    simulation_args = {"run_name": run_name, "role_names": role_names, **general_settings, **permutation}
    print(simulation_args)

    os.environ.update(simulation_args)
    docker_client.compose.pull()
    docker_client.compose.up(abort_on_container_exit=True,
                             services=simulation_services)
    docker_client.compose.down()


def main():
    args = parse_arguments()
    general_settings, run_settings = load_config(Path(args.config))
    general_settings, simulation_services, convert_services = prepare_general_settings(
        general_settings)
    docker_client = setup_docker_client()

    try:
        if "permutation_settings" in run_settings:
            permutation_settings = run_settings["permutation_settings"]
            permutation_settings[
                "sensors_config_files"] = validate_sensors_config_files(
                    permutation_settings["sensors_config_files"])
            num_executions = int(permutation_settings.pop("num_executions", 1))
            # Calculate all possible combinations of simulation configs
            keys, values = zip(*permutation_settings.items())
            permutations = [
                dict(zip(keys, v)) for v in itertools.product(*values)
            ]
            logging.info(
                f"Running {len(permutations) * num_executions} different simulation setups..."
            )
            for _ in range(num_executions):
                for permutation in permutations:
                    try:
                        simulate_single_permutation(docker_client,
                                                    general_settings,
                                                    permutation,
                                                    simulation_services)
                    except DockerException:
                        docker_client.compose.down()
    except KeyboardInterrupt:
        docker_client.compose.kill()


if __name__ == "__main__":
    main()
