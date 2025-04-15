#!/usr/bin/env python3

import argparse
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
        default='./config/data-driven-development-demo-permutation-execution.yml',
        help=('Config file which should be used (default:'
              './config/data-driven-development-demo-permutation-execution.yml)'))
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


def prepare_controller(simulation_setup: dict[str, Any]) -> dict[str, Any]:
    # Store relevant keys as simulation controller args
    controller_args = []
    argument_list = ["spawn_point", "town", "weather", "vehicle_number", "vehicle_occupancy", "walker_number"]

    for key in list(simulation_setup.keys()):
        if key in argument_list:
            controller_args.append(f"--{key} {simulation_setup[key]}")

    simulation_setup["controller_args"] = " ".join(controller_args)
    return simulation_setup


def prepare_scenario(simulation_setup: dict[str, Any]) -> dict[str, Any]:
    if "scenario_file" in simulation_setup:
        scenario_file = simulation_setup.pop("scenario_file")

        # validate scenario_file
        validate_file(scenario_file, ".xosc")

        # split scenario_file in scenario_file and scenario_path
        simulation_setup["scenario_folder"] = os.path.dirname(scenario_file)
        simulation_setup["scenario_file"] = os.path.basename(scenario_file)

        # get town from scenario file
        tree = ET.parse(scenario_file)
        root = tree.getroot()
        elem = root.find('./RoadNetwork/LogicFile')
        simulation_setup["town"] = elem.get('filepath')

    return simulation_setup


def setup_docker_client(docker_compose_file: Path = Path(
    './docker-compose.yml')) -> DockerClient:
    if not docker_compose_file.exists():
        logging.error(f"Docker Compose file not found: {docker_compose_file}")
        sys.exit(1)
    return DockerClient(compose_files=[docker_compose_file])


def validate_file(file: str, suffix: str = None) -> str:
    if not file:
        logging.error("No file specified")
        sys.exit(1)

    file = Path(file)
    if not file.is_file():
        logging.error(f"File not found: {file}")
        sys.exit(1)

    if suffix and file.suffix != suffix:
        logging.error(f"Invalid file suffix: {file}")
        sys.exit(1)

    return str(file)


def get_role_names(sensor_config_file: str) -> str:
    try:
        with open(sensor_config_file) as file:
            data = json.load(file)
        role_names = [actor["id"] for actor in data["objects"] if actor["type"].startswith("vehicle.")]
        role_names = " ".join(role_names)
        return role_names
    except json.JSONDecodeError as e:
        logging.error(f"Error reading JSON file: {e}")
        sys.exit(1)


def simulate_setup(docker_client: DockerClient,
                                general_settings: dict[Any],
                                simulation_setup: dict[Any],
                                simulation_services: list[str]) -> None:
    run_name = '_'.join(
        Path(str(value)).stem if Path(str(value)).parent != Path('.') else str(value)
        for value in simulation_setup.values()
    )

    simulation_setup["sensors_config_files"] = validate_file(
                simulation_setup["sensors_config_files"], ".json")
    simulation_setup["role_names"] = get_role_names(simulation_setup["sensors_config_files"])

    simulation_setup = prepare_controller(simulation_setup)
    simulation_setup = prepare_scenario(simulation_setup)

    simulation_args = {"run_name": run_name, **general_settings, **simulation_setup}

    os.environ.update(simulation_args)
    docker_client.compose.pull()
    docker_client.compose.up(abort_on_container_exit=True,
                             services=simulation_services)
    docker_client.compose.down()


def check_run_settings(run_settings: dict[Any], simulation_services: list[str]) -> None:
    config_checks = {
        "permutation_settings": {
            "required_service": "carla-simulation-controller",
            "forbidden_service": "carla-scenario-runner",
            "error_message": "simulation-controller is required for permutation execution."
        },
        "scenario_settings": {
            "required_service": "carla-scenario-runner",
            "forbidden_service": "simulation-controller",
            "error_message": "carla-scenario-runner is required for scenario execution."
        }
    }

    for setting_key, config in config_checks.items():
        if setting_key in run_settings:
            if (config["required_service"] not in simulation_services or
                config["forbidden_service"] in simulation_services):
                logging.error(config["error_message"])
                sys.exit(1)

def main():
    args = parse_arguments()
    general_settings, run_settings = load_config(Path(args.config))
    general_settings, simulation_services, convert_services = prepare_general_settings(
        general_settings)
    docker_client = setup_docker_client()

    try:
        num_executions = int(run_settings.pop("num_executions", 1))

        check_run_settings(run_settings, simulation_services)

        simulation_setups = []
        for setting_key in ("permutation_settings", "scenario_settings"):
            if setting_key in run_settings:
                keys, values = zip(*run_settings[setting_key].items())
                setups = [dict(zip(keys, v)) for v in itertools.product(*values)]
                simulation_setups.extend(setups)

        logging.info(
            f"Running {len(simulation_setups) * num_executions} different simulation setups..."
        )

        for _ in range(num_executions):
            for simulation_setup in simulation_setups:
                try:
                    simulate_setup(docker_client,
                                                general_settings,
                                                simulation_setup,
                                                simulation_services)
                except DockerException:
                    docker_client.compose.down()

    except KeyboardInterrupt:
        docker_client.compose.kill()


if __name__ == "__main__":
    main()
