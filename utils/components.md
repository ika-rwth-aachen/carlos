# CARLA Components

This document aims to give a brief overview of the components provided by [carla-components.yml](../carla-components.yml). 

## Component List

| Service Name | Repository | Variations | Notes |
| --- | --- | --- | --- |
| `carla-server` | [fb-fi/simulation/carla/carla](https://gitlab.ika.rwth-aachen.de/fb-fi/simulation/carla/carla) | offscreen | - |
| `carla-ros-bridge` | [fb-fi/simulation/carla/ros-bridge](https://gitlab.ika.rwth-aachen.de/fb-fi/simulation/carla/ros-bridge) | - | - |
| `carla-scenario-runner` | [fb-fi/simulation/carla/carla_scenario_runner_ros](https://gitlab.ika.rwth-aachen.de/fb-fi/simulation/carla/carla_scenario_runner_ros) | - | - |
| `ros-monitoring` | [fb-fi/its-modules/monitoring/ros-monitoring](https://gitlab.ika.rwth-aachen.de/fb-fi/its-modules/monitoring/ros-monitoring) | - | - |

## carla-simulator

This service represents a single instance of a [CARLA](http://carla.org/) simulator. It can be used in a variety of ways, often in conjunction with [ROS](https://www.ros.org/) and can be seen as the basis of setups that aim to simulate and test automated driving features.

Starting this service (e.g. by `docker compose up carla-sever` in this folder) should open up a new GUI window in which you can move around the currently loaded map and follow what is happening in simulations.

### carla-simulator-offscreen

Basically the same as the normal service, with the exception that no GUI window is opened and thus one cannot directly follow what is happening on the map.

The upside to this is that this service is a bit lighter on the GPU and does not clutter up your screen as much. Especially useful when only interested in simulation without direct graphical output.

### carla-simulator-healthcheck

Acts as an intermediate between a CARLA simulator instance and services/apps that depend on that instances health. In essence, it is a continually running python-client, that has its health check configured to run a script that tests the connection towards a specified CARLA simulator in certain intervals.

Since the health of this service depends on the availability of the CARLA simulator, other services can depend on this services health to ensure a correct startup and shutdown order and thus preventing them from attempting to connect to the simulator before it is started or after it is stopped.

**Note:** This only helps with startup and shutdown order. Your applications still need to have their own logic for handling connection fails during operation

## carla-ros-bridge

The task of the `carla-ros-bridge` is to close the gap between the ROS communication system and the CARLA simulator itself. It achieves this by acting as an interface. Firstly, by connecting to a running CARLA server, retrieving relevant data (e.g. from [sensors](https://carla.readthedocs.io/projects/ros-bridge/en/latest/ros_sensors/)) and information (e.g. world info) and then publishing it via topics in the [CARLA messages](https://carla.readthedocs.io/projects/ros-bridge/en/latest/ros_msgs/) format. Secondly, by subscribing to some topics (e.g. weather_control) and offering services (e.g. spawn_object) which the ROS nodes can utilize to influence the simulation.

Including a `carla-ros-bridge` into your setup is mandatory when said setup uses both CARLA and ROS and needs them to interact.

## carla-scenario-runner

Simulators like CARLA are often used to run, monitor and evaluate pre-defined scenarios. This is where the [carla-scenario-runner](https://github.com/carla-compose/carla-scenario-runner) comes in. It allows you to run scenarios defined through a Python interface, or under the [OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) standard.

[comment]: # (The `carla-scenario-runner-ros` service extends this to ROS by adding a node that provides a ROS service through which other ROS nodes can request execution of specified scenarios and publishing the status of the execution via a topic. It also provides a compact launch file with which the scenario runner will be launched and a specified scenario could instantly be executed.)

## ros-monitoring

This services provides a possibility for monitoring data within the ROS world. All message definitions are preinstalled together with monitoring tools such as RViz. Hence, visualization of CARLA, but also custom messages becomes possible by the `ros-monitoring` service. Make sure that all GUI forwarding settings are enables.