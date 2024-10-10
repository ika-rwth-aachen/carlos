#!/usr/bin/env python3

import os
import json
import yaml
import itertools
import argparse
import xml.etree.ElementTree as ET
from python_on_whales import DockerClient
from python_on_whales import DockerException


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        metavar='C',
        default='./config/data-driven-development-demo-image-segmentation.yaml',
        help=(
            'Config file which should be used (default:'
            './config/data-driven-development-demo-image-segmentation.yaml)'))
    args = parser.parse_args()
    return args


def read_yaml_config(config_file_path):
    # get configs from yaml file
    with open(config_file_path) as config_file:
        config = yaml.safe_load(config_file)
    setting_configs = config["settings"]
    simulation_configs = config["simulation_configs"]
    return setting_configs, simulation_configs


def setup_docker():
    # setup docker compose file and path
    docker_compose_file = './docker-compose.yml'
    return DockerClient(compose_files=[docker_compose_file])


def set_flag(config, value):
    new_value = "--{} {}".format(value, config[value])
    config[value] = new_value
    return config


def flat_record_topics(config):
    record_topics = config.pop("record_topics")
    record_topics_arg = " ".join(record_topics.values())
    config["record_topics_arg"] = record_topics_arg
    return config


def read_sensor_config(config):
    with open(config["sensors_config"]) as sensors_config_file:
        sensors_config = json.load(sensors_config_file)
    return sensors_config


def set_vehicle_ids(sensor_config, setting_config):
    vehicle_ids = ','.join([
        obj['id'] for obj in sensor_config['objects']
        if obj['type'].startswith('vehicle.')
    ])
    setting_config["role_names"] = vehicle_ids
    return setting_config


def generate_data(docker, play_args, setting_configs):
    os.environ.update(play_args)
    # explicitely pull the images before to enable Ubuntu 20.04 compatibility
    docker.compose.pull()
    docker.compose.up(abort_on_container_exit=True,
                      services=setting_configs["simulation_services"])
    docker.compose.down()


def set_numb_exec(config):
    # setup execution number
    if "num_executions" in config:
        num_executions = int(config["num_executions"])
    else:
        num_executions = 1
    config.pop("num_executions", None)
    return num_executions, config


def set_sensor_config(permutation_configs):
    sensors_config_files = get_file_path_list(permutation_configs,
                                              "sensors_config_files",
                                              "sensors_config_folder", ".json")
    permutation_configs.pop("sensors_config_files", None)
    permutation_configs.pop("sensors_config_folder", None)
    permutation_configs["sensors_config"] = sensors_config_files
    return permutation_configs


def get_file_path_list(configs, file_configs, folder_config, file_extension):
    filepaths = []

    # Add files from the file_configs section if present
    filepaths.extend(configs.get(file_configs, []))

    # Check if folder_config exists and is valid
    folder_path = configs.get(folder_config)
    if folder_path and os.path.exists(folder_path):
        filepaths.extend(
            os.path.join(folder_path, item) for item in os.listdir(folder_path)
            if item.endswith(file_extension))

    return filepaths


def get_key_config_perm(sim_conf_perm):
    key_config_permutation = {
        key: value
        for key, value in sim_conf_perm.items() if key != "sensors_config"
    }
    return key_config_permutation


def get_run_key_names(key_config_permutation):
    run_name = '_'.join(
        [str(value) for value in key_config_permutation.values()])
    key_config_string = ' '.join(
        [f'--{key} {value}' for key, value in key_config_permutation.items()])
    return run_name, key_config_string


def get_town(scenario_filepath):
    tree = ET.parse(scenario_filepath)
    root = tree.getroot()
    logic_file_elem = root.find('./RoadNetwork/LogicFile')
    town = logic_file_elem.get('filepath')
    return town


def flatten_settings_config_edit(setting_configs):
    settings_configs_edit = setting_configs.copy()
    settings_configs_edit.pop("simulation_services", None)
    settings_configs_edit.pop("convert_services", None)
    return settings_configs_edit


def run_scenario(docker, scenario_filepath, setting_configs,
                 sensor_conf_filepath):
    # get name of the town from xosc file
    town = get_town(scenario_filepath)
    filename = scenario_filepath.split('/')[-1]

    settings_configs_edit = flatten_settings_config_edit(setting_configs)

    settings_configs_edit["scenario_folder"] = os.path.dirname(
        scenario_filepath)

    scenario_args = {
        "run_name": filename,
        "town": town,
        "scenario": filename,
        "sensors_config": sensor_conf_filepath,
        **settings_configs_edit
    }

    print("Starting data generation with scenario: {}".format(filename))
    generate_data(docker, scenario_args, setting_configs)
    print("Finished scenario: {} with sensors_config: {}".format(
        filename, sensor_conf_filepath))


def run_single_permutation(docker, simulation_config_permutation,
                           setting_configs):
    key_config_permutation = get_key_config_perm(simulation_config_permutation)
    run_name, key_config_string = get_run_key_names(key_config_permutation)

    sensors_config = read_sensor_config(simulation_config_permutation)
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
    num_executions, permutation_configs = set_numb_exec(permutation_configs)

    # load all possible combinations of simulation configs
    keys, values = zip(*permutation_configs.items())
    simulation_config_permutations = [
        dict(zip(keys, v)) for v in itertools.product(*values)
    ]

    print("Running all {} different simulation setups...".format(
        len(simulation_config_permutations) * num_executions))

    # iterate over all simulation config combinations
    for i in range(num_executions):
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

    num_executions, scenario_configs = set_numb_exec(scenario_configs)

    print("Number of Scenarios executed: {}".format(
        len(scenario_files) * len(sensors_config_files) * num_executions))

    # loop over execution number, sensor.json files and scenarios
    for i in range(num_executions):
        for sensors_config_filepath in sensors_config_files:
            # get role names from sensor.json file
            sensors_config = read_sensor_config(sensors_config_filepath)
            setting_configs = set_vehicle_ids(sensors_config, setting_configs)

            for scenario_filepath in scenario_files:
                if scenario_filepath.endswith(".xosc"):
                    try:
                        run_scenario(docker, scenario_filepath,
                                     setting_configs, sensors_config_filepath)
                    except DockerException:
                        docker.compose.down()


def yaml_setup(config_file_path):
    setting_configs, simulation_configs = read_yaml_config(config_file_path)
    docker = setup_docker()

    # update time args for time_controller
    if "max_real_time" in setting_configs:
        setting_configs = set_flag(setting_configs, "max_real_time")
    if "max_simulation_time" in setting_configs:
        setting_configs = set_flag(setting_configs, "max_simulation_time")

    # create data folders if it does not exist yet and save path in
    # setting_configs
    if "output_path" not in setting_configs:
        setting_configs["output_path"] = "./data/"

    #TODO: Warum output_path und output_bag_path miot gleichem Wert??
    if "record_topics" in setting_configs:
        output_bag_path = setting_configs["output_path"]
        if not os.path.exists(output_bag_path):
            os.makedirs(output_bag_path)
        setting_configs["output_bag_path"] = output_bag_path

    # flatten settings
    if "record_topics" in setting_configs:
        setting_configs = flat_record_topics(setting_configs)

    return docker, simulation_configs, setting_configs


def main():
    args = parse_arguments()
    # get configs of yaml file
    docker, simulation_configs, setting_configs = yaml_setup(args.config)

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
