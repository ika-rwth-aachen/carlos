<img src="../utils/images/data-driven-development-icon.png" height=100 align="right">

# Use Case: *Data-Driven Development*

>[!NOTE]
> **Background**: The *data-driven development* use case covers development processes using large amounts of data, which are not effectively obtainable in real-world settings, thus motivating simulations. For many applications, simulative data can be sufficiently accurate to be integrated into the data-driven development process. This includes training data for machine learning algorithms but also closed-loop reinforcement learning. Potentially interesting data includes raw sensor but also dynamic vehicle data in a wide variety at large scale. Simulations additionally enable data generation beyond the physical limits of vehicle dynamics or sensor configurations. To accumulate large amounts of data, relevant simulation parameters can be automatically sampled along different dimensions. Subsequently, automation and parallelization empower a cost-effective execution of multiple simulations, especially when using already established orchestration tools.

The subsequent demonstration showcases rapid *data driven development* and specifically addresses the following requirements:
- high simulation **fidelity**
- **flexibility** and containerization
- automation and **scalability**

## Prerequisites

> [!IMPORTANT]  
> Make sure that all [system requirements](../utils/requirements.md) are fulfilled.
> Additionally, a Python installation is required on the host for this use case. We recommend using [conda](https://docs.conda.io/projects/conda/en/stable/index.html).

Install and activate the conda environment:

```bash
conda env install -f env/environment.yml
conda activate carlos_data_driven_development
```

Alternatively, you can also use Pip:

```bash
pip install -r requirements.txt
```

## Data Generation

In the initial demo [software-prototyping](../software-prototyping), we demonstrated the integration of a Function Under Test (FUT) with CARLOS, exploring its capabilities through practical experimentation. While these tests validated the general functionality of our image segmentation module,  it became clear that there is considerable potential to improve its performance. Given that this module, like many AD functions, relies heavily on machine learning models trained with specific datasets, the quality and quantity of this training data are crucial.

### Permutation-based Data Generation

Given that the specific nature of the data is less critical, the main objective is to generate as much and diverse data as possible. This can be effectively achieved through permutations of the simulation parameters, ensuring both quantity and diversity in the generated dataset.

Run the demo for permutation-based data generation:
```bash
# carlos/data-driven-development$
python ./data_generation.py --config data-driven-delevopment-demo-image-segmentation.json
```

or use the top-level `run-demo.sh` script:
```bash
# carlos$
./run-demo.sh data-driven-delevopment
```

In addition to the already known components, we are introducing the `carla-client` here. This component enables the invocation of custom scripts through CARLA's PythonAPI, offering flexible configuration options for the simulation.

Thus, data generation at large scale becomes possible and helps developers to achive diverse and useful data for any application.

### Scenario-based Data Generation

Assuming we improved our model, we are now aiming to evaluate its performance in targeted, real-world scenarios. Hence, we need to generate data in such concrete scenarios, for which the scenario-based data generation feature can be utilized. In this example, we demonstrate how a list of multiple OpenSCENARIO files can be integrated into the data generation pipeline as well to generate data under those specific conditions.

```bash
# carlos/data-driven-development$
python ./data_generation.py --config data-driven-delevopment-demo-scenario-execution.json
```

All scenarios are executed sequentially and data is generated analogous to above. The respective configuration file contains mainly a path or list to specific predefined OpenSCENARIO files: 
```json
"simulation_configs":
    {
        "scenario_configs": 
        {
            "execution_number": 1,
            "scenario_files": ["../utils/scenarios/town01.xosc", "../utils/scenarios/town10.xosc"],
            "sensors_config_files": ["./config/sensors/rgb_segmentation_camera.json"]
        }
    }
```

Following on that initial scenario-based simulation approach, we focus more on the automatic execution and evaluation of scenarios at large scale in the third, [automatic testing demo](../automated-testing/README.md). In addition, a full integration into a CI workflow is provided.


### Configuration Parameters

The JSON configuration file for the data generation pipeline consists of two main sections: `settings` and `simulation_configs`. The `settings` section specifies general parameters. The `simulation_configs` section must either contain `permutation_configs` for permutation-based simulations or `scenario_configs` for scenario-based simulations.

#### General settings (`settings`)

| Name | Description | Note | required | default
| --- | --- | --- | --- | --- |
| `max_simulation_time` | Maximum simulation-time duration in seconds of one simulation run before it is terminated |  | not required | 300 |
| `max_real_time` | Maximum real-time duration in seconds of one simulation run before it is terminated |  | not required | 300 |
| `simulation_services` | List of all Docker services which should are executed during a simulation run | Names must match with the service names in [docker-compose.yml](./docker-compose.yml) | required | - |
| `record_topics` | Dict of ROS 2 topics to be recorded | | not required | - |
| `output_path` | Path for storing generated data |  | not required | `./data/` |

#### Permutation settings (`permutation_configs`)
| Name | Description | Note | required | default
| --- | --- | --- | --- | --- |
| `num_executions` | Number of times a simulation based on a single permutation is executed | Must be an integer | not required | 1 |
| `sensors_config_files` | List of sensor configuration files | | not required | - |
| `sensors_config_folder` | List of directories containing sensor configuration files |  | not required | - |
| `spawn_point` | List of spawnpoints for the data-generating-vehicle | Only numbers are allowed | required | - |
| `town` | List of towns for the simulation environment | [Town list](https://carla.readthedocs.io/en/latest/core_map/#non-layered-maps), Town10 = Town10HD | not required | Town01 |
| `vehicle_number` | List of numbers that spawn a fixed number of vehicles | only used if `vehicle_occupancy` is not set, vehicles are spawned via generate_traffic.py | not required | - |
| `vehicle_occupancy` | List of numbers between 0 and 1 that spawn vehicles proportionally to the number of available spawn points | vehicles are spawned via generate_traffic.py | not required | - |
| `weather` | List of weather conditions | [Weather conditions list](https://github.com/carla-simulator/carla/blob/master/PythonAPI/docs/weather.yml#L158) | not required | depends on town, in general "ClearSunset" |

#### Scenario settings
| Name | Description | Note | required | default
| --- | --- | --- | --- | --- |
| `num_executions` | Number of times a simulation based on a single permutation is executed | Must be an integer | not required | 1 |
| `scenario_files` | List of OpenScenario files (.xosc) | | not required | - |
| `scenario_folder` | List of directories containing OpenScenario files (.xosc) | | not required | - |
| `sensors_config_files` | List of sensor configuration files | | not required | - |
| `sensors_config_folder` | List of directories containing sensor configuration files |  | not required | - |
