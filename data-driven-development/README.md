<img src="../utils/images/data-driven-development-icon.png" height=100 align="right">

# Use Case: *Data-Driven Development*

>[!NOTE]
> **Background**: The *data-driven development* use case covers development processes using large amounts of data, which are not effectively obtainable in real-world settings, thus motivating simulations. For many applications, simulative data can be sufficiently accurate to be integrated into the data-driven development process. This includes training data for machine learning algorithms but also closed-loop reinforcement learning. Potentially interesting data includes raw sensor but also dynamic vehicle data in a wide variety at large scale. Simulations additionally enable data generation beyond the physical limits of vehicle dynamics or sensor configurations. To accumulate large amounts of data, relevant simulation parameters can be automatically sampled along different dimensions. Subsequently, automation and parallelization empower a cost-effective execution of multiple simulations, especially when using already established orchestration tools.


## Getting Started

> [!IMPORTANT]  
> Make sure that all [system requirements](../utils/requirements.md) are fulfilled.
> Additionally, a python installation is required on the host for this use case. We recommend using [conda](https://docs.conda.io/projects/conda/en/stable/index.html).

Install and activate the conda environment:

```bash
conda env install -f env/environment.yml
conda activate carlos_data_driven_development
```

Alternatively, you can also use pip:

```bash
pip install -r requirements.txt
```

### Permutation-based data generation

This example picks up where the [software-prototyping](../software-prototyping/README.md) example left off. In the previous example an image segmentation perception function was introduced. As this function is based on a neural network, it needs sufficient training data to work reliable. Here comes this demo into play. Upon execution, a large data set of a vehicle's front camera images along with their corresponding semantic segmentations are generated.

```bash
python ./data_generation.py --config data-driven-delevopment-demo-image-segmentation.json
```

The data is generated based on a set configuration parameters from which a set of all possible permutations is generated. For more information, have a look at the [config guide](config/config.md).

In addition to the already known components, we are introducing the `carla-client` here. With this component it is possible to invoke custom script utilizing CARLA's PythonAPI to configure the simulation.

> [!NOTE]
> A detailed description of the individual components can be found in [components guide](../utils/components.md).

### Scenario-based data generation

It is also possible to pass a list of OpenScenario files to the demo, from which the data are generated.

```bash
python ./data_generation.py --config data-driven-delevopment-demo-scenario-execution.json
```
