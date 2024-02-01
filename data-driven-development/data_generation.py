import os
import glob
import json
import itertools
import argparse
import xml.etree.ElementTree as ET
from python_on_whales import DockerClient, DockerException

def start_permutation_simulations(docker, permutation_configs, setting_configs):
    # get different sensor.json configs
    sensors_config_files = getFilePathList(permutation_configs, "sensors_config_files", "sensors_config_folder", ".json")
    permutation_configs.pop("sensors_config_files", None)
    permutation_configs.pop("sensors_config_folder", None)
    permutation_configs["sensors_config"] = sensors_config_files

    # setup execution number
    if "num_executions" in permutation_configs:
        num_executions = int(permutation_configs["num_executions"])
    else:
        num_executions = 1
    permutation_configs.pop("num_executions", None)

    # load all possible combinations of simulation configs
    keys, values = zip(*permutation_configs.items())
    simulation_config_permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print("Running all {} different simulation setups...".format(len(simulation_config_permutations) * num_executions))

    # iterate over all simulation config combinations
    for i in range(num_executions):
        for simulation_config_permutation in simulation_config_permutations:
            try:
                key_config_permutation = {key: value for key, value in simulation_config_permutation.items() if key != "sensors_config"}
                run_name = '_'.join([str(value) for value in key_config_permutation.values()])
                key_config_string = ' '.join([f'--{key} {value}' for key, value in key_config_permutation.items()])

                with open(simulation_config_permutation["sensors_config"]) as sensors_config_file:
                    sensors_config = json.load(sensors_config_file)
                    vehicle_ids = ','.join([obj['id'] for obj in sensors_config['objects'] if obj['type'].startswith('vehicle.')])
                    setting_configs["role_names"] = vehicle_ids

                settings_configs_edit = setting_configs.copy()
                settings_configs_edit.pop("simulation_services", None)
                settings_configs_edit.pop("convert_services", None)

                # environment variables for docker-compose-arguments
                simulation_args = {
                    "run_name": run_name,
                    "key_config_string": key_config_string,
                    **simulation_config_permutation,
                    **settings_configs_edit
                }

                # update environment variables to pass to docker-compose-file
                print("Starting data generation with Config: {}".format(simulation_args))
                os.environ.update(simulation_args)
                docker.compose.up(abort_on_container_exit=True, services=setting_configs["simulation_services"], pull='always')
                docker.compose.down() 

                print("Config finished!")

            except DockerException:
                docker.compose.down() 

# def start_scenario_runner_simulations(docker, scenario_configs, setting_configs):
#     sensors_config_files = getFilePathList(scenario_configs, "sensors_config_files", "sensors_config_folder", ".json")
#     scenario_files = getFilePathList(scenario_configs, "scenario_files", "scenario_folder", ".xosc")

#     if "num_executions" in scenario_configs:
#         num_executions = int(scenario_configs["num_executions"])
#     else:
#         num_executions = 1

#     print("Number of Scenarios executed: {}".format(len(scenario_files) * len(sensors_config_files) * num_executions))
    
#     # loop over execution number, sensor.json files and scenarios
#     for i in range(num_executions):
#         for sensors_config_filepath in sensors_config_files:
#             # get role names from sensor.json file
#             with open(sensors_config_filepath) as sensors_config_file:
#                 sensors_config = json.load(sensors_config_file)
#                 vehicle_ids = ','.join([obj['id'] for obj in sensors_config['objects'] if obj['type'].startswith('vehicle.')])
#                 setting_configs["role_names"] = vehicle_ids
            
#             for scenario_filepath in scenario_files:
#                 if scenario_filepath.endswith(".xosc"):
#                     try:
#                         # get name of the town from xosc file
#                         tree = ET.parse(scenario_filepath)
#                         root = tree.getroot()
#                         logic_file_elem = root.find('./RoadNetwork/LogicFile')
#                         town = logic_file_elem.get('filepath')
#                         filename = os.path.splitext(scenario_filepath.split('/')[-1])[0]
                            
#                         settings_configs_edit = setting_configs.copy()
#                         settings_configs_edit.pop("simulation_services", None)
#                         settings_configs_edit.pop("convert_services", None)
#                         settings_configs_edit["scenario_folder"] = os.path.dirname(scenario_filepath)

#                         scenario_args = {
#                             "run_name": filename,
#                             "town": town,
#                             "scenario": filename,
#                             "sensors_config": sensors_config_filepath,
#                             **settings_configs_edit
#                         }

#                         print("Starting data generation with scenario: {}".format(filename))
#                         os.environ.update(scenario_args)
#                         docker.compose.up(abort_on_container_exit=True, services=setting_configs["simulation_services"], pull='always')
#                         docker.compose.down() 
#                         print("Finished scenario: {} with sensors_config: {}".format(filename, sensors_config_filepath))

#                     except DockerException:
#                         docker.compose.down() 

def getFilePathList(configs, file_configs, folder_config, file_extension):
    filepaths = []

    if file_configs in configs:
        for file_config in configs[file_configs]:
            filepaths.append(file_config)

    if folder_config in configs and os.path.exists(configs[folder_config]):
        folder_contents = os.listdir(configs[folder_config])
        for item in folder_contents:
            if item.endswith(file_extension):
                item_path = os.path.join(configs[folder_config], item)
                filepaths.append(item_path)

    return filepaths

def setup(config_file_path):
    # get config from json file
    with open(config_file_path) as config_file:
        config = json.load(config_file)

        setting_configs = config["settings"]

        simulation_configs = config["simulation_configs"]

        # setup docker compose file and path
        docker_compose_file = './docker-compose.yml'
        docker = DockerClient(compose_files=[docker_compose_file])

        # update time args for time_controller
        if "max_real_time" in setting_configs:
            setting_configs["max_real_time"] = "--max_real_time {}".format(setting_configs["max_real_time"])
        if "max_simulation_time" in setting_configs:
            setting_configs["max_simulation_time"] = "--max_simulation_time {}".format(setting_configs["max_simulation_time"])

        # create data folders if it does not exist yet and save path in setting_configs
        if "output_path" not in setting_configs:
            setting_configs["output_path"] = "./data/"
        
        if "record_topics" in setting_configs:
            output_bag_path = setting_configs["output_path"] + "bags"
            if not os.path.exists(output_bag_path):
                os.makedirs(output_bag_path)
            setting_configs["output_bag_path"] = output_bag_path

        # flatten settings
        if "record_topics" in setting_configs:
            record_topics = setting_configs.pop("record_topics")
            record_topics_arg = ""
            for record_topic in record_topics.values():
                record_topics_arg += "{} ".format(record_topic)
            setting_configs["record_topics_arg"] = record_topics_arg
            setting_configs.update(record_topics)

        return docker, simulation_configs, setting_configs

def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '--config',
        metavar='C',
        default='./config/data-driven-delevopment-demo.json',
        help='Config file which should be used (default: ./config/data-driven-delevopment-demo.json)')
    args = argparser.parse_args()

    # get configs from json file
    docker, simulation_configs, setting_configs = setup(args.config)
    
    try:
        # Start scenarios from path if path is set
        # TODO
        # if "scenario_configs" in simulation_configs:
        #     print("Simulating scenarios with scenario_runner...")
        #     start_scenario_runner_simulations(docker, simulation_configs["scenario_configs"], setting_configs)

        # Start the simulations defined in config
        if "permutation_configs" in simulation_configs:
            print("Simulating defined setups...")
            start_permutation_simulations(docker, simulation_configs["permutation_configs"], setting_configs)

    except KeyboardInterrupt:
        docker.compose.kill()

if __name__ == "__main__":
    main()
