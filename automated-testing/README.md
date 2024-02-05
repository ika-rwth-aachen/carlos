<img src="../utils/images/automated-testing-icon.png" height=100 align="right">

# Use Case: *Automated testing*

>[!IMPORTANT]
> **TODO**: This README is a working document and not finalized. A detailed description of all features within the demo is provided as soon as possible.

>[!NOTE]
> **Background**: In the *automated testing* demo, simulation is considered to systematically evaluate a large number of defined tests, potentially within the safety assurance process. A specific test configuration may encompass both a concrete scenario and well-defined test metrics for evaluation. Thus, a direct interface to a standardized scenario database is favorable, and custom pass-fail criteria need to be configurable to deduce objective test results. Scalability drastically improves efficiency when simulating multiple test configurations. Moreover, embedding the simulation architecture in a CI process further accelerates the entire safety assurance.

The subsequent demonstration showcases *automated testing* and specifically addresses the following requirements:
- prefedined scenario metrics and **automatic evaluation **
- automation and **scalability**
- CI integration with **GitHub actions and workflows**

## Getting Started

> [!IMPORTANT]  
> Make sure that all [system requirements](../utils/requirements.md) are fulfilled.

Directly start the use case demonstration using the top-level `run-demo.sh` script:

```bash
./run-demo.sh automated-testing
```

### Manual Testing Pipeline

- scripts for sequential scenario execution

### Automatic CI Pipeline

#### Actions

- we provide open GitHub actions for CARLOS
  - scenario setup
  - scenario exectution

#### Workflow

- demo workflow
  - example scenario catalogue
  - screenshot

### Outlook: Parallelization using Orchestration Tools
