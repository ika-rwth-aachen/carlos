# Components

This document aims to give a brief overview of the various Docker services provided by [components.yml](./components.yml) and utilized within the CARLOS use cases. 

## Component List

| Service Name | Repository | Docker Image |
| --- | --- | --- |
| `carla-simulator` | [ika-rwth-aachen/carla](https://github.com/ika-rwth-aachen/carla) | rwthika/carla-simulator:server |
| `carla-client` | [ika-rwth-aachen/carla](https://github.com/ika-rwth-aachen/carla) | rwthika/carla-simulator:client |
| `carla-ros-bridge` | [ika-rwth-aachen/ros-bridge](https://github.com/ika-rwth-aachen/ros-bridge) | rwthika/carla-ros-bridge |
| `carla-scenario-runner` | [ika-rwth-aachen/carla_scenario_runner_ros](https://github.com/ika-rwth-aachen/carla_scenario_runner_ros) | rwthika/carla-scenario-runner |
| `ros-monitoring` | [ika-rwth-aachen/docker-ros-ml-images](https://github.com/ika-rwth-aachen/docker-ros-ml-images?tab=readme-ov-file#rwthikaros2-cuda-ros-2--cuda) | rwthika/ros2-cuda:humble-desktop-full |


## carla-simulator

This Docker service represents a single instance of a [CARLA](http://carla.org/) simulator and constitutes the central element of the framework that aim to simulate and test automated driving features.

Starting this service (e.g. by `docker compose up carla-simulator` in this folder) should open up a new GUI window in which you can move around the currently loaded map and follow what is happening in simulations.

In addition, the Docker services provides a continuous health check monitoring if the CARLA server is running and connection can be established. Since the health of this service depends on the availability of the CARLA simulator, other services can depend on this services health to ensure a correct startup and shutdown order and thus preventing them from attempting to connect to the simulator before it is started or after it is stopped.

**Note:** This only helps with startup and shutdown order. Your applications still need to have their own logic for handling connection fails during operation


### carla-simulator-offscreen
This Docker service is a variation of the previous carla-simulator service, with the exception that no GUI window is opened and thus one cannot directly follow what is happening on the map.

The upside to this is that this service is a bit lighter on the GPU and does not clutter up your screen as much. Especially useful when only interested in simulation without direct graphical output.


## carla-client
The carla-client Docker services provides a minimal solution to interact with the CARLA server via PythonAPI. In addition, all example scripts are contained and can be used even with GUI access enabled. Thus, powerful demonstrations can be shown solely with a server and this carla-client Docker service.


## carla-ros-bridge
The carla-ros-bridge is the Docker service that facilitates the powerful combination of CARLA and ROS  by acting as an interface. It retrieves relevant data (e.g. [sensor data](https://carla.readthedocs.io/projects/ros-bridge/en/latest/ros_sensors/)) from the simulation to publish it on ROS topics in the [CARLA messages](https://carla.readthedocs.io/projects/ros-bridge/en/latest/ros_msgs/) format. Simultaneously the service is listening on different topics for requested actions, which are translated to commands to be executed in CARLA.

Including a carla-ros-bridge into your setup is mandatory when said setup uses both CARLA and ROS and needs them to interact.


## carla-scenario-runner
To enable scenario-based testing and evaluation, the carla-scenario-runner Docker service is used. It provides the scenario-runner a powerful engine that follows the [OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) standard for scenario definitions. This enables efficient scenario execution and additional metric evaluation, enabling an automatic scenario assessment.

Including a carla-scenario-runner into your setup is mandatory when you want to simulate a more complex, concrete scenario.


## ros-monitoring
This services provides a possibility for monitoring data within the ROS world. All [common_msgs](http://wiki.ros.org/common_msgs) definitions are preinstalled together with monitoring tools such as RViz. Make sure that all GUI forwarding settings are enabled.

### ros-monitoring-offscreen
This Docker service is a variation of the previous ros-monitoring service, with the exception that no GUI window is opened and thus one cannot use visualization tools such as RViz. However, this is sufficient for any other lightweight ROS tasks.
