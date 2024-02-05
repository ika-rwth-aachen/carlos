<img src="../utils/images/automated-testing-icon.png" height=100 align="right">

# Use Case: *Automated testing*

>[!NOTE]
> **Background**: In the *automated testing* demo, simulation is considered to systematically evaluate a large number of defined tests, potentially within the safety assurance process. A specific test configuration may encompass both a concrete scenario and well-defined test metrics for evaluation. Thus, a direct interface to a standardized scenario database is favorable, and custom pass-fail criteria need to be configurable to deduce objective test results. Scalability drastically improves efficiency when simulating multiple test configurations. Moreover, embedding the simulation architecture in a CI process further accelerates the entire safety assurance.

The subsequent demonstration showcases *automated testing* and specifically addresses the following requirements:
- prefedined scenario metrics and **automatic evaluation **
- automation and **scalability**
- CI integration with **GitHub actions and workflows**

## Getting Started

> [!IMPORTANT]  
> Make sure that all [system requirements](../utils/requirements.md) are fulfilled.
> Additionally, this Demo requires a [self-hosted GitHub Runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) to execute scenarios within a CI workflow. The specific requirements for such a runner are listed [below](#self-hosted-github-runner).

This demo aims to automatically evaluate predefined test scenarios. For this purpose, a test catalog can be defined using OpenSCENARIO files as contained in the [scenarios](../utils/scenarios) folder. These scenarios can be simulated and evaluated using the [carla-scenario-runner](). Thus, a basic [docker-compose setup]() only includes the carla-simulator and a carla-scenario-runner Docker service. So, in general, the demo enables the efficient execution of multiple scenario-based tests with CARLA, both in local environments and within an automated GitHub CI process.

### Manual Testing Pipeline

In your local environment, you can evaluate mutiple scnearios directly, usind the provided top-level `run-demo.sh` script:

```bash
./run-demo.sh automated-testing
```

- scripts for sequential scenario execution

### Automatic CI Pipeline

#### Actions

- we provide open GitHub actions for CARLOS
  - scenario setup
  - scenario exectution

#### Workflow

#### Self-Hosted GitHub Runner

- demo workflow
  - example scenario catalogue
  - screenshot

### Outlook: Parallelization using Orchestration Tools
