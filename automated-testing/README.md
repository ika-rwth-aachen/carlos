<img src="../utils/images/automated-testing-icon.png" height=100 align="right">

# Use Case: *Automated testing*

>[!NOTE]
> **Background**: In the *automated testing* demo, simulation is considered to systematically evaluate a large number of defined tests, potentially within the safety assurance process. A specific test configuration may encompass both a concrete scenario and well-defined test metrics for evaluation. Thus, a direct interface to a standardized scenario database is favorable, and custom pass-fail criteria need to be configurable to deduce objective test results. Scalability drastically improves efficiency when simulating multiple test configurations. Moreover, embedding the simulation architecture in a CI process further accelerates the entire safety assurance.

The subsequent demonstration showcases *automated testing* and specifically addresses the following requirements:
- predefined scenario metrics and **automatic evaluation**
- automation and **scalability**
- CI integration with **GitHub actions and workflows**

## Getting Started

> [!IMPORTANT]  
> Make sure that all [system requirements](../utils/requirements.md) are fulfilled.
> Additionally, this demo requires a [self-hosted GitHub Runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) to execute scenarios within a CI workflow. The specific requirements for such a runner are listed [below](#self-hosted-github-runner).

This demo aims to automatically evaluate predefined test scenarios. For this purpose, a test catalog can be defined using OpenSCENARIO files as contained in the [scenarios](../utils/scenarios) folder. These scenarios can be simulated and evaluated using the [carla-scenario-runner](https://github.com/ika-rwth-aachen/carla-scenario-runner). Thus, a basic [docker-compose template](./template.yml) only includes the `carla-simulator` and a `carla-scenario-runner` Docker service. So, in general, the demo enables the efficient execution of multiple scenario-based tests with CARLA, both in local environments and within an automated GitHub CI process.

### Manual Testing Pipeline

In your local environment, you can evaluate multiple scenarios directly, using the provided top-level `run-demo.sh` script:

```bash
# carlos$
./run-demo.sh automated-testing
```
or
```bash
# carlos/automated-testing$
./evaluate-scenarios.sh
```

### Automatic CI Pipeline

All scenarios within the test catalog are also simulated and evaluated in an automatic [CI pipeline on GitHub](https://github.com/ika-rwth-aachen/carlos/actions/workflows/automated-testing.yml). A detailed look in the [scenarios folder](../utils/scenarios/) shows that a few of them have the postfix `.opt` marking them as optional. This means a failure in test evaluation is allowed for those specific scenarios. The CI pipeline processes required scenarios first, and than considered all optional scenarios. In both cases a job matrix is generated before consecutive jobs are created to simulate the specific scenario. As an example, a workflow is shown below.

<p align="center"><img src="../utils/images/automated-testing-workflow.png" width=800></p>

#### Actions

- we provide open [GitHub actions](../.github/actions/) for CARLOS
  - [evaluate-scenario](../.github/actions/evaluate-scenario/)
  - [generate-job-matrix](../.github/actions/generate-job-matrix/)

#### Workflow

- analog to the local evaluation script, we provide a GitHub workflow
  - [automated-testing.yml](../.github/workflows/automated-testing.yml)

#### Self-Hosted GitHub Runner

- demo workflow
  - example scenario catalogue
  - screenshot

### Outlook - Scalability using Orchestration Tools
