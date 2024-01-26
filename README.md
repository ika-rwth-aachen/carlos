# *TODO* – A Modular Simulation Framework for Agile Development and Scenario-based Testing of Automated Vehicles

<img src="utils/images/logo.png" height=180 align="right">

This repository accompanies our paper on a modular simulation framework in the context of automated vehicles. It provides a containerized and modular simulation enviornment based on the open simulator CARLA and utilizes a simple integration of ROS applications. Following our paper, it provides useful examples for the three use cases: 
  - [Agile Development](./agile-development/)
  - [Data Generation](./data.generation/)
  - [Safety Assurance](./safety-assurance/)

The repository is structured as follows:
- [Publication](#publication)
- [Getting Started](#getting-started)
- [Simulation Architecture](#simulation-architecture)
  - [Simulation Core](#simulation-core)
  - [Communication Module](#communication-module)
  - [Control Module](#control-module)
- [Acknowledgements](#acknowledgements)

## Publication

> ***TODO* – A Modular Simulation Framework for Agile Development and Scenario-based Testing of Automated Vehicles**  
> ([*arXiv*](TODO))
>
> [Christian Geller](https://www.ika.rwth-aachen.de/de/institut/team/fahrzeugintelligenz-automatisiertes-fahren/geller.html), [Benedikt Haas](TODO), [Amarin Kloeker](https://www.ika.rwth-aachen.de/de/institut/team/fahrzeugintelligenz-automatisiertes-fahren/akleoker.html), [Lutz Eckstein](https://www.ika.rwth-aachen.de/de/institut/team/univ-prof-dr-ing-lutz-eckstein.html)  
> [Institute for Automotive Engineering (ika), RWTH Aachen University](https://www.ika.rwth-aachen.de/en/)
> 
> <sup>*Abstract* – Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</sup>

---

## Getting Started

**Note:** Check out the comprehensive [tutorial](./utils/tutorial.md), which gives an overview of the main simulation framework features, combining CARLA, Docker and ROS.

This repository provides demos which can be used as example or initial starting point. They contain the CARLA server GUI, but also ROS based components. A demo can be started using the provided script:

```bash
./run-demo.sh agile-development
```

After you are done, hitting <kbd>CTRL</kbd> + <kbd>C</kbd> twice is enough because the provided `run-demo.sh` does the entire cleanup.

| Use Case | Integrated Components | Description |
| ------ | ------                | ------ 
| [***agile-development***](./agile-development/README.md) | CARLA, carla-ros-bridge, rviz | Runs examplaric carla-ros-bridge. |
| [***data-generation***](./data-generation/README.md) | CARLA, carla-ros-bridge, carla-scenario-runner | Run multiple random simulations to caputre sensor data. |
| [***safety-assurance***](./safety-assurance/README.md) | CARLA, carla-scenario-runner | Enables OpenSCENARIO execution |


## Simulation Architecture

<img src="utils/images/architecture.png" height=500 align="left">

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.


**Note**: For all of our use case examples we will be utilizing predefined Docker services, listed in [carla-components.yml](./carla-components.yml) and further described in the [carla-components overview](./utils/carla-components.md).

The proposed architecture uses basic components which mainly rely on public forks of the original [CARLA ecosystem](https://github.com/carla-simulator/). We extended those repository by additional GitHub CI workflows to generate minimal Docker images used in the overall architecture.


### Simulation Core: [***carla-simulator***](https://github.com/carla-compose/carla-simulator)
<p align="left">
  <img src="https://img.shields.io/github/v/release/carla-compose/carla-simulator"/></a>
  <img src="https://img.shields.io/github/license/carla-compose/carla-simulator"/>
  <a href="https://github.com/carla-compose/carla-simulator/actions/workflows/docker.yml"><img src="https://github.com/carla-compose/carla-simulator/actions/workflows/docker.yml/badge.svg"/></a>
  <img src="https://img.shields.io/badge/CARLA-0.9.15-blueviolet"/>
  <img src="https://img.shields.io/github/stars/carla-compose/carla-simulator?style=social"/>
</p>

### Communication Module: [***carla-ros-bridge***](https://github.com/carla-compose/carla-ros-bridge)
<p align="left">
  <img src="https://img.shields.io/github/v/release/carla-compose/carla-ros-bridge"/></a>
  <img src="https://img.shields.io/github/license/carla-compose/carla-ros-bridge"/>
  <a href="https://github.com/carla-compose/carla-ros-bridge/actions/workflows/docker.yml"><img src="https://github.com/carla-compose/carla-ros-bridge/actions/workflows/docker.yml/badge.svg"/></a>
  <img src="https://img.shields.io/badge/ROS 2-humble-blueviolet"/>
  <img src="https://img.shields.io/github/stars/carla-compose/carla-ros-bridge?style=social"/>
</p>

### Control Module: [***carla-scenario-runner***](https://github.com/carla-compose/carla-scenario-runner)
<p align="left">
  <img src="https://img.shields.io/github/v/release/carla-compose/carla-scenario-runner"/>
  <img src="https://img.shields.io/github/license/carla-compose/carla-scenario-runner"/>
  <a href="https://github.com/carla-compose/carla-scenario-runner/actions/workflows/docker.yml"><img src="https://github.com/carla-compose/carla-scenario-runner/actions/workflows/docker.yml/badge.svg"/></a>
  <img src="https://img.shields.io/badge/CARLA-0.9.15-blueviolet"/>
  <img src="https://img.shields.io/badge/Python-3.10-blueviolet"/>
  <img src="https://img.shields.io/github/stars/carla-compose/carla-scenario-runner?style=social"/>
</p>


## Acknowledgements

This work is accomplished within the project [AUTOtech.*agil*](https://www.ika.rwth-aachen.de/en/competences/projects/automated-driving/autotech-agil-en.html) (FKZ 01IS22088A). We acknowledge the financial support for the projects by the Federal Ministry of Education and Research of Germany (BMBF).
