# Data-driven development configuration parameters

The configuration of the data generation pipeline is based on a JSON file. Two examples are provided within this directory.

While the current implementation is limited to the specified settings, it is easily possible to extend the [provided code](../src/) according to your own requirements.

<table>
  <tr>
    <th>JSON Key</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>settings</code></td>
    <td>Dictionary containing the general settings</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>max_simulation_time</code></td>
    <td>Maximum time in seconds of one simulation run</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>max_real_time</code></td>
    <td>Maximum real time in seconds one simulation run is allowed to execute before being aborted</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>simulation_services</code></td>
    <td>List of Docker services used in the simulation</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>record_topics</code></td>
    <td>Dictionary of topics to be recorded</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>output_path</code></td>
    <td>Path for storing generated data</td>
  </tr>
  <tr>
    <td><code>simulation_configs</code></td>
    <td>Dictionary containing the simulation specific configuration parameters</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>permutation_configs</code></td>
    <td>Dictionary of configuration parameters from which the simulation permutations are generated</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>num_executions</code></td>
    <td>Number of times a simulation based on a single permutation is executed</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>sensors_config_files</code></td>
    <td>List of sensor configuration files</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>spawn_point</code></td>
    <td>List of spawn points for the simulation</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>town</code></td>
    <td>List of towns for the simulation environment</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>vehicle_occupancy</code></td>
    <td>Occupancy rate of randomly spawned vehicles</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>walker_number</code></td>
    <td>Number of walkers in the simulation</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>weather</code></td>
    <td>List of weather conditions for the simulation</td>
  </tr>
  <tr>
    <td style="padding-left: 2em;"><code>scenario_configs</code></td>
    <td>Dictionary of configuration parameters for defining simulation scenarios</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>num_executions</code></td>
    <td>Number of times a simulation based on a single permutation is executed</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>scenario_files</code></td>
    <td>List of OpenScenario files</td>
  </tr>
  <tr>
    <td style="padding-left: 4em;"><code>sensors_config_files</code></td>
    <td>List of sensor configuration files specific to scenarios</td>
  </tr>
</table>
