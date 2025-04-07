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


def setup_docker_client(docker_compose_file: Path = Path(
    './docker-compose.yml')) -> DockerClient:
    if not docker_compose_file.exists():
        logging.error(f"Docker Compose file not found: {docker_compose_file}")
        sys.exit(1)
    return DockerClient(compose_files=[docker_compose_file])


def update_flag(config: dict[str, Any], value: str) -> dict[str, Any]:
    new_value = f"--{value} {config[value]}"
    config[value] = new_value
    return config


def flatten_record_topics(config: dict[str, Any]) -> dict[str, Any]:
    record_topics = config.pop("record_topics")
    config["record_topics_arg"] = " ".join(record_topics.values())
    return config


def read_sensor_config(config_path: Path) -> dict[str, Any]:
    try:
        with config_path.open() as sensors_config_file:
            return json.load(sensors_config_file)
    except FileNotFoundError:
        logging.error(f"Sensor config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error reading sensor config file file: {e}")
        sys.exit(1)


def set_vehicle_ids(sensor_config: dict[str, Any],
                    setting_config: dict[str, Any]) -> dict[str, Any]:
    vehicle_ids = ','.join(obj['id'] for obj in sensor_config['objects']
                           if obj['type'].startswith('vehicle.'))
    setting_config["role_names"] = vehicle_ids
    return setting_config


def generate_data(docker: DockerClient, play_args: dict[str, str],
                  setting_configs: dict[str, Any]) -> None:
    os.environ.update(play_args)
    # Explicitely pull the images before to enable Ubuntu 20.04 compatibility
    docker.compose.pull()
    docker.compose.up(abort_on_container_exit=True,
                      services=setting_configs["simulation_services"])
    docker.compose.down()


def set_num_executions(config: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    num_executions = int(config.pop("num_executions", 1))
    return num_executions, config


def set_sensor_config(permutation_configs: dict[str, Any]) -> dict[str, Any]:
    sensors_config_files = get_file_path_list(permutation_configs,
                                              "sensors_config_files",
                                              "sensors_config_folder", ".json")
    permutation_configs.pop("sensors_config_files", None)
    permutation_configs.pop("sensors_config_folder", None)
    permutation_configs["sensors_config"] = sensors_config_files
    return permutation_configs


def get_file_path_list(configs: dict[str, Any], file_key: str, folder_key: str,
                       file_extension: str) -> list[Path]:
    filepaths = configs.get(file_key, [])
    if folder_path := configs.get(folder_key):
        folder = Path(folder_path)
        if folder.is_dir():
            filepaths.extend(
                folder / item for item in folder.iterdir()
                if item.is_file() and item.suffix == file_extension)
    return filepaths


def get_key_config_permutation(
        simulation_config_permuation: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in simulation_config_permuation.items()
        if key != "sensors_config"
    }


def get_run_key_names(
        key_config_permutation: dict[str, Any]) -> tuple[str, str]:
    run_name = '_'.join(
        [str(value) for value in key_config_permutation.values()])
    key_config_string = ' '.join(
        [f'--{key} {value}' for key, value in key_config_permutation.items()])
    return run_name, key_config_string


def get_town(scenario_filepath: Path) -> str:
    try:
        tree = ET.parse(scenario_filepath)
        root = tree.getroot()
        if (logic_file_elem := root.find('./RoadNetwork/LogicFile')) is None:
            raise ValueError(
                "LogicFile element containing town filepath not found in OpenScenario file"
            )
        if (town := logic_file_elem.get('filepath', None)) is None:
            raise ValueError("Town filepath not found in OpenScenario file")
        return town
    except FileNotFoundError:
        logging.error(f"OpenScenario file not found: {scenario_filepath}")
        sys.exit(1)
    except ET.ParseError as e:
        logging.error(f"Error parsing OpenScenario file: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"{e}")
        sys.exit(1)


def run_scenario(docker: DockerClient, scenario_filepath: Path,
                 setting_configs: dict, sensor_conf_filepath: Path) -> None:
    town = get_town(scenario_filepath)
    filename = scenario_filepath.name

    scenario_args = {
        key: value
        for key, value in setting_configs.items()
        if key not in ("simulation_services", "convert_services")
    }

    scenario_args.update({
        "scenario_folder": str(scenario_filepath.parent),
        "run_name": filename,
        "town": town,
        "scenario": filename,
        "sensors_config": str(sensor_conf_filepath),
    })

    logging.info(f"Starting data generation with scenario: {filename}")
    generate_data(docker, scenario_args, setting_configs)
    logging.info(
        f"Finished scenario: {filename} with sensors_config: {sensor_conf_filepath}"
    )


def run_single_permutation(docker, simulation_config_permutation,
                           setting_configs):
    key_config_permutation = get_key_config_perm(simulation_config_permutation)
    run_name, key_config_string = get_run_key_names(key_config_permutation)

    sensors_config = read_sensor_config(
        Path(simulation_config_permutation["sensors_config"]))
    setting_configs = set_vehicle_ids(sensors_config, setting_configs)

    settings_configs_edit = flatten_settings_config_edit(setting_configs)

    # environment variables for docker-compose-arguments
    simulation_args = {
        "run_name": run_name,
        "key_config_string": key_config_string,
        **simulation_config_permutation,
        **settings_configs_edit
    }

    # update environment variables to pass to docker-compose-file
    print("Starting data generation with Config: {}".format(simulation_args))
    generate_data(docker, simulation_args, setting_configs)
    print("Config finished!")


def start_permutation_simulations(docker, permutation_configs,
                                  setting_configs):
    permutation_configs = set_sensor_config(permutation_configs)

    # setup execution number
    num_executions, permutation_configs = set_num_executions(
        permutation_configs)

    # load all possible combinations of simulation configs
    keys, values = zip(*permutation_configs.items())
    simulation_config_permutations = [
        dict(zip(keys, v)) for v in itertools.product(*values)
    ]

    logging.info(
        f"Running all {len(simulation_config_permutations) * num_executions} different simulation setups..."
    )

    for _ in range(num_executions):
        for simulation_config_permutation in simulation_config_permutations:
            try:
                run_single_permutation(docker, simulation_config_permutation,
                                       setting_configs)
            except DockerException:
                docker.compose.down()


def start_scenario_runner_simulations(docker, scenario_configs,
                                      setting_configs):
    sensors_config_files = get_file_path_list(scenario_configs,
                                              "sensors_config_files",
                                              "sensors_config_folder", ".json")
    scenario_files = get_file_path_list(scenario_configs, "scenario_files",
                                        "scenario_folder", ".xosc")

    num_executions, scenario_configs = set_num_executions(scenario_configs)

    print("Number of Scenarios executed: {}".format(
        len(scenario_files) * len(sensors_config_files) * num_executions))

    # loop over execution number, sensor.json files and scenarios
    for i in range(num_executions):
        for sensors_config_filepath in sensors_config_files:
            # get role names from sensor.json file
            sensors_config = read_sensor_config(Path(sensors_config_filepath))
            setting_configs = set_vehicle_ids(sensors_config, setting_configs)

            for scenario_filepath in scenario_files:
                if scenario_filepath.endswith(".xosc"):
                    try:
                        run_scenario(docker, scenario_filepath,
                                     setting_configs, sensors_config_filepath)
                    except DockerException:
                        docker.compose.down()


def yaml_setup(config_file_path):
    setting_configs, simulation_configs = load_config(config_file_path)
    docker = setup_docker()

    # update time args for time_controller
    if "max_real_time" in setting_configs:
        setting_configs = update_flag(setting_configs, "max_real_time")
    if "max_simulation_time" in setting_configs:
        setting_configs = update_flag(setting_configs, "max_simulation_time")

    # create data folders if it does not exist yet and save path in
    # setting_configs
    if "output_path" not in setting_configs:
        setting_configs["output_path"] = "./data/"

    if "record_topics" in setting_configs:
        output_bag_path = setting_configs["output_path"]
        if not os.path.exists(output_bag_path):
            os.makedirs(output_bag_path)
        setting_configs["output_bag_path"] = output_bag_path

    # flatten settings
    if "record_topics" in setting_configs:
        setting_configs = flatten_record_topics(setting_configs)

    return docker, simulation_configs, setting_configs


def main():
    args = parse_arguments()
    general_settings, run_settings = load_config(Path(args.config))
    docker_client = setup_docker_client()
    
    docker, simulation_configs, setting_configs = yaml_setup(Path(args.config))

    try:
        # Start scenarios from path if path is set
        if "scenario_configs" in simulation_configs:
            print("Simulating scenarios with scenario_runner...")
            start_scenario_runner_simulations(
                docker, simulation_configs["scenario_configs"],
                setting_configs)

        # Start the simulations defined in config
        if "permutation_configs" in simulation_configs:
            print("Simulating defined setups...")
            start_permutation_simulations(
                docker, simulation_configs["permutation_configs"],
                setting_configs)

    except KeyboardInterrupt:
        docker.compose.kill()


if __name__ == "__main__":
    main()
