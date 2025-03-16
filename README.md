# Optimos V2

The next generation of [Optimos](https://github.com/AutomatedProcessImprovement/roptimus-prime). A Resource, Roster and Batching optimizer using Prosimos simulator.

# Evaluation

## Overview

This report includes data for the following **agents**, **models**, and **modes**. Click on a model to jump to its section.

#### Agents

- Proximal Policy Optimization
- Proximal Policy Optimization Random
- Simulated Annealing
- Simulated Annealing Random
- Tabu Search
- Tabu Search Random

#### Models

- [Bpi Challenge 2012](#bpi-challenge-2012)
- [Bpi Challenge 2017](#bpi-challenge-2017)
- [Bpic2019 Das](#bpic2019-das)
- [Callcentre](#callcentre)
- [Consulta Data Mining](#consulta-data-mining)
- [Gov](#gov)
- [Insurance](#insurance)
- [Production](#production)
- [Purchasing Example](#purchasing-example)
- [Sepsis Das](#sepsis-das)
- [Trafic Das](#trafic-das)

#### Modes

- Easy (Batching gives a large benefit to processing time)
- Mid (Batching gives a balanced benefit to processing time)
- Hard (Batching does not give a benefit to processing time)

---

## Metrics Explanation

Below is an explanation of the metrics used in this report. Note that one simulation (or 'Solution') corresponds to one step on the x-axis.

<ul>
<li><strong>Pareto Front Size:</strong> Number of solutions in the current Pareto Front.</li>
<li><strong>Explored Solutions:</strong> Total number of solutions for which all neighbors have been explored.</li>
<li><strong>New Base Solutions (Radius):</strong> Potential new base solution within a small radius. Only relevant for Tabu Search/Hill-Climbing to mitigate simulation error/variance.</li>
<li><strong>New Base Solutions (Temperature):</strong> Potential new base solutions within the temperature radius. Only relevant for Simulated Annealing.</li>
<li><strong>Median Batch Processing Time:</strong> Median task processing time per batch instance.</li>
<li><strong>Median Wait+Idle Time:</strong> Median waiting plus idle time per task instance.</li>
<li><strong>Min Wait+Idle Time:</strong> Minimum waiting plus idle time per task instance.</li>
<li><strong>Min Batch Processing Time:</strong> Minimum processing time per batch instance.</li>
<li><strong>Average Cycle Time:</strong> Average cycle time (from first enablement to the end of last activity) of all solutions in the current Pareto Front.</li>
<li><strong>Min Cycle Time:</strong> Minimum cycle time among all solutions in the current Pareto Front.</li>
<li><strong>Iteration Number:</strong> In one iteration, multiple mutations are performed. Depending on the agent, the solutions will be treated differently. Note that the number of solutions per iteration is not the same for all agents.</li>
</ul>

## Bpi Challenge 2012

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                35 |                559 |                           0 |                                  |                      271.506 |               2876.58 |            1066.82 |                   84.1198 |        1.23741e+06 |     1.2117e+06 |              390 |
| Simulated Annealing                 |                39 |                454 |                             |                               27 |                      146.801 |               12994.7 |            1021.14 |                   38.8925 |        1.30261e+06 |    1.20913e+06 |              602 |
| Proximal Policy Optimization        |                46 |               1020 |                             |                                  |                      143.251 |               5429.32 |            1284.11 |                   9.84884 |        1.22262e+06 |     1.1635e+06 |            10000 |
| Proximal Policy Optimization Random |                41 |               1347 |                             |                                  |                      172.202 |               4790.51 |            1057.49 |                    30.207 |        1.21544e+06 |    1.16689e+06 |            10000 |
| Tabu Search Random                  |                 8 |                 35 |                           0 |                                  |                      410.999 |               1849.46 |            1146.99 |                   283.828 |        1.27674e+06 |    1.21298e+06 |               22 |
| Simulated Annealing Random          |                26 |                459 |                             |                                0 |                      327.659 |               9863.57 |            1117.53 |                   104.251 |         1.3469e+06 |    1.21027e+06 |              307 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                18 |                354 |                             |                                0 |                      400.248 |               62184.1 |             995.72 |                   179.726 |        1.58524e+06 |    1.21104e+06 |              242 |
| Simulated Annealing                 |                26 |                456 |                             |                                0 |                      467.688 |               6320.09 |            964.332 |                   273.924 |        1.41545e+06 |    1.21131e+06 |              565 |
| Tabu Search                         |                25 |                297 |                           0 |                                  |                       414.72 |               6866.26 |            931.426 |                   231.571 |        1.52894e+06 |    1.21731e+06 |              168 |
| Tabu Search Random                  |                16 |                 65 |                           0 |                                  |                      302.327 |               65421.7 |             916.78 |                   103.398 |         1.7864e+06 |    1.21133e+06 |               62 |
| Proximal Policy Optimization        |                22 |               1748 |                             |                                  |                      416.373 |               58168.2 |            1023.32 |                   125.748 |        7.74888e+06 |    1.17014e+06 |            10000 |
| Proximal Policy Optimization Random |                28 |               1209 |                             |                                  |                      314.348 |               63653.1 |            831.471 |                   115.456 |        4.82441e+06 |     1.1663e+06 |            10000 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                41 |               1754 |                             |                                  |                      381.689 |               6475.52 |            1309.49 |                   55.4108 |        1.42909e+06 |       1.17e+06 |            10000 |
| Simulated Annealing                 |                35 |                696 |                             |                                9 |                      325.567 |               29975.7 |             1019.1 |                   105.748 |        1.37587e+06 |    1.21377e+06 |              642 |
| Tabu Search Random                  |                15 |                 50 |                           0 |                                  |                      436.944 |               15197.9 |            1274.86 |                   158.886 |        1.38085e+06 |    1.21129e+06 |               45 |
| Tabu Search                         |                17 |                146 |                           0 |                                  |                      327.359 |               18741.5 |            1241.84 |                    216.94 |        1.36132e+06 |    1.21358e+06 |              133 |
| Simulated Annealing Random          |                20 |                429 |                             |                                0 |                      402.162 |               10419.2 |            1074.47 |                   172.256 |        1.39163e+06 |    1.21732e+06 |              255 |
| Proximal Policy Optimization Random |                38 |               1677 |                             |                                  |                      358.013 |               9448.71 |            1054.15 |                   41.6873 |        1.46688e+06 |       1.17e+06 |            10000 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2012_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Bpi Challenge 2017

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                34 |               1495 |                             |                              564 |                      187.678 |                2671.3 |            1685.37 |                   88.4875 |             941853 |         847722 |              655 |
| Proximal Policy Optimization        |                40 |               2296 |                             |                                  |                      76.9091 |               5744.85 |             1880.5 |                   26.7912 |             851855 |         622342 |            10000 |
| Tabu Search Random                  |                19 |                285 |                           0 |                                  |                      161.651 |               2953.78 |            1847.12 |                   81.3977 |             899299 |         851318 |              208 |
| Tabu Search                         |                39 |               2778 |                         829 |                                  |                       84.846 |               4172.09 |            1863.92 |                   47.1866 |             878877 |         696456 |              548 |
| Simulated Annealing Random          |                19 |                641 |                             |                                0 |                      187.088 |               2868.49 |            1666.28 |                   74.1311 |             869780 |         850046 |              398 |
| Proximal Policy Optimization Random |                33 |               3480 |                             |                                  |                       70.704 |                5654.5 |            1594.65 |                   26.1549 |             846913 |         773073 |            10000 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                16 |                734 |                             |                                  |                      264.749 |                124297 |            1565.19 |                    238.49 |         1.9778e+07 |         838174 |             6309 |
| Proximal Policy Optimization Random |                12 |                649 |                             |                                  |                      312.849 |               85486.2 |            1578.08 |                   253.508 |        1.71763e+07 |         837243 |             5499 |
| Tabu Search                         |                 2 |                  5 |                           1 |                                  |                      345.837 |               1913.78 |            1633.79 |                    322.47 |             853221 |         852804 |                4 |
| Simulated Annealing Random          |                 7 |                494 |                             |                                0 |                      289.753 |               3270.74 |             1669.1 |                   191.397 |        1.04407e+06 |         851497 |              300 |
| Tabu Search Random                  |                 4 |                 13 |                           0 |                                  |                      346.008 |               1940.38 |            1886.98 |                   300.681 |             884157 |         852467 |               10 |
| Simulated Annealing                 |                25 |               2069 |                             |                              211 |                      282.783 |               16583.8 |             1546.3 |                    162.47 |             974249 |         845163 |              698 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                21 |                511 |                             |                                0 |                      229.168 |                 48541 |            1687.05 |                   157.022 |        1.11572e+06 |         850648 |              317 |
| Tabu Search Random                  |                11 |                 85 |                           0 |                                  |                      272.658 |               5366.21 |            1733.68 |                   182.011 |        1.12352e+06 |         852813 |               59 |
| Simulated Annealing                 |                26 |                835 |                             |                              115 |                      232.291 |               17700.8 |            1552.83 |                    165.44 |             955819 |         846219 |              684 |
| Tabu Search                         |                36 |               1426 |                         563 |                                  |                      261.936 |               4764.39 |               1631 |                   149.707 |             924136 |         846409 |              599 |
| Proximal Policy Optimization Random |                32 |               1668 |                             |                                  |                      256.863 |               4246.43 |             1567.9 |                   162.776 |             933243 |         838151 |             9105 |
| Proximal Policy Optimization        |                32 |               1505 |                             |                                  |                      256.137 |               3996.74 |            1730.14 |                   142.168 |        1.02846e+06 |         825269 |            10000 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpi_Challenge_2017_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Bpic2019 Das

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpic2019_Das_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpic2019_Das_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                19 |                  2 |                             |                                  |                      497.189 |               70454.2 |            22196.1 |                   274.656 |         1.1639e+07 |    1.08201e+06 |             2019 |
| Simulated Annealing                 |                 6 |                202 |                             |                              938 |                       3349.8 |               20885.9 |            17427.8 |                   2674.79 |         1.5071e+06 |    1.06311e+06 |              591 |
| Simulated Annealing Random          |                 8 |               1077 |                             |                               20 |                       1470.7 |                 13291 |            11772.4 |                   710.565 |         2.4995e+06 |    1.06716e+06 |              868 |
| Tabu Search                         |                 2 |                 38 |                        1255 |                                  |                      1345.84 |               11600.6 |            7859.27 |                   1344.12 |        1.58991e+06 |    1.37119e+06 |              176 |
| Tabu Search Random                  |                 1 |                153 |                           0 |                                  |                      1205.18 |               8067.77 |            8067.77 |                   1205.18 |         1.7469e+06 |     1.7469e+06 |              155 |
| Proximal Policy Optimization Random |                21 |                  2 |                             |                                  |                      72.7355 |               85031.5 |            32568.2 |                   19.6215 |        1.22195e+07 |     1.6904e+06 |             4077 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Bpic2019_Das_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpic2019_Das_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpic2019_Das_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                12 |                193 |                             |                             1695 |                      6826.63 |               54250.2 |            40890.1 |                   5813.41 |        2.19567e+06 |    1.00062e+06 |              502 |
| Proximal Policy Optimization        |                 3 |                  8 |                             |                                  |                      880.522 |               75071.4 |            67806.2 |                   622.467 |        2.08606e+07 |    5.14389e+06 |              640 |
| Tabu Search                         |                20 |                161 |                        1055 |                                  |                      6379.16 |               58697.1 |              39942 |                   5753.88 |        3.98648e+06 |    1.42871e+06 |              425 |
| Proximal Policy Optimization Random |                13 |                  2 |                             |                                  |                      1087.13 |               85264.4 |            73515.1 |                   74.9752 |        1.97393e+09 |    3.22863e+06 |              780 |
| Simulated Annealing Random          |                 2 |                297 |                             |                                0 |                       1478.5 |                122153 |            60686.6 |                   1289.17 |        6.59939e+06 |    3.35898e+06 |              254 |
| Tabu Search Random                  |                 5 |                 34 |                           0 |                                  |                       6848.5 |               57649.6 |            45475.6 |                   5950.38 |        2.48004e+06 |    1.00068e+06 |               40 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Bpic2019_Das_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Bpic2019_Das_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Bpic2019_Das_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                18 |                  1 |                             |                                  |                      3966.08 |                260646 |            38356.2 |                   397.863 |        1.79178e+08 |    2.15193e+06 |             2550 |
| Simulated Annealing Random          |                 9 |                423 |                             |                                0 |                       4911.1 |               41088.3 |            34011.4 |                   1215.16 |        1.77198e+08 |    2.04851e+06 |              347 |
| Proximal Policy Optimization        |                12 |                  1 |                             |                                  |                      1302.29 |           1.36772e+06 |            41748.2 |                   543.183 |        2.89777e+08 |    3.21102e+06 |              250 |
| Tabu Search                         |                 8 |                 96 |                         280 |                                  |                       4414.2 |               24713.4 |            19788.5 |                   4007.29 |        4.26219e+06 |    3.04265e+06 |              346 |
| Simulated Annealing                 |                 7 |                200 |                             |                             2726 |                      5448.91 |               33277.7 |            29834.5 |                   4860.56 |        1.95637e+06 |    1.54438e+06 |              593 |
| Tabu Search Random                  |                 1 |                  5 |                           0 |                                  |                      5195.05 |               37198.8 |            37198.8 |                   5195.05 |        2.07682e+06 |    2.07682e+06 |                7 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Bpic2019_Das_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Bpic2019_Das_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Callcentre

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Callcentre_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Callcentre_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Callcentre_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Callcentre_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                11 |                326 |                             |                                  |                      8.50276 |               1002.91 |            52.8721 |                   2.71642 |            12413.4 |        1951.83 |             5250 |
| Simulated Annealing                 |                 7 |                360 |                             |                             1088 |                      635.292 |               73685.2 |            62330.9 |                   475.886 |         1.7386e+06 |     1.3876e+06 |              664 |
| Proximal Policy Optimization        |                17 |                405 |                             |                                  |                       2.0621 |                9.2528 |            4.74002 |               0.000273994 |            73793.5 |        1881.05 |             6610 |
| Simulated Annealing Random          |                11 |               1314 |                             |                              542 |                      44.0033 |               52849.9 |            949.004 |                    18.734 |         1.5341e+07 |         191679 |              868 |
| Tabu Search                         |                 1 |                  4 |                           0 |                                  |                      394.564 |               39471.6 |            39471.6 |                   394.564 |        1.52795e+06 |    1.52795e+06 |               21 |
| Tabu Search Random                  |                 9 |               1536 |                         356 |                                  |                      412.834 |               30917.8 |            27420.2 |                   289.078 |        1.19836e+06 |    1.06623e+06 |              868 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Callcentre_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Callcentre_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Callcentre_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Callcentre_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Callcentre_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                 5 |                311 |                             |                                0 |                      5159.47 |                565748 |             561513 |                   4975.99 |        1.02421e+07 |    9.80554e+06 |              468 |
| Simulated Annealing Random          |                15 |               1339 |                             |                              655 |                      46.2151 |               17433.5 |            481.313 |                    28.908 |             172392 |        4876.96 |              868 |
| Tabu Search Random                  |                 3 |                 16 |                           0 |                                  |                      167.355 |           1.45963e+06 |             672983 |                   142.055 |        1.98113e+07 |    1.10522e+07 |               18 |
| Proximal Policy Optimization Random |                 8 |                590 |                             |                                  |                      66.8742 |               1518.69 |            545.972 |                   64.4603 |            15676.6 |        4562.45 |             4357 |
| Tabu Search                         |                 1 |                  4 |                           0 |                                  |                      5408.31 |                614176 |             614176 |                   5408.31 |        1.02259e+07 |    1.02259e+07 |                9 |
| Proximal Policy Optimization        |                10 |                349 |                             |                                  |                      63.5844 |               1546.46 |            553.247 |                 0.0032952 |            45649.9 |        4417.33 |             3520 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Callcentre_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Callcentre_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Callcentre_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Callcentre_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Callcentre_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Callcentre_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                 4 |                129 |                         323 |                                  |                      2627.52 |                404183 |             265318 |                   2134.67 |         9.4731e+06 |    8.71964e+06 |              221 |
| Tabu Search Random                  |                 2 |                 11 |                           0 |                                  |                      4027.36 |                508363 |             484184 |                    4020.2 |        9.01121e+06 |    8.77325e+06 |               14 |
| Proximal Policy Optimization Random |                12 |                494 |                             |                                  |                      56.7506 |               18992.3 |             2501.6 |                   48.9149 |            80850.5 |        34311.6 |             9004 |
| Simulated Annealing Random          |                 9 |               1290 |                             |                              671 |                      62.0692 |               23664.1 |            387.522 |                    27.257 |             191474 |        4281.56 |              868 |
| Simulated Annealing                 |                 4 |                389 |                             |                               52 |                      3260.93 |                389294 |             328432 |                   2023.79 |        7.95649e+06 |    7.09316e+06 |              668 |
| Proximal Policy Optimization        |                 5 |                 84 |                             |                                  |                        59.71 |               382.555 |            336.071 |                   56.9189 |            6096.85 |        5758.89 |             2116 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing Random</th>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Callcentre_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Callcentre_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Consulta Data Mining

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                42 |               3770 |                        1811 |                                  |                      170.106 |               17030.1 |            6137.59 |                   110.896 |        1.14301e+07 |    1.06536e+07 |              497 |
| Simulated Annealing                 |                26 |                897 |                             |                             2623 |                      265.373 |               13104.2 |            5840.44 |                   180.957 |        1.15301e+07 |    1.08998e+07 |              505 |
| Simulated Annealing Random          |                34 |                953 |                             |                                0 |                      225.732 |               12859.9 |            6329.29 |                   133.415 |        1.15087e+07 |     1.0908e+07 |              656 |
| Tabu Search Random                  |                29 |                292 |                           0 |                                  |                      155.542 |               39696.6 |            6169.77 |                   93.8181 |        1.19551e+07 |    1.10942e+07 |              200 |
| Proximal Policy Optimization        |                52 |               1806 |                             |                                  |                      103.127 |               34976.8 |            6015.03 |                   37.7386 |        1.15599e+07 |    1.05594e+07 |             6620 |
| Proximal Policy Optimization Random |                33 |               1536 |                             |                                  |                      154.911 |               25812.6 |            6631.31 |                    46.425 |        1.16295e+07 |    1.07297e+07 |             6960 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Consulta_Data_Mining_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                10 |                480 |                             |                                0 |                      362.548 |               37494.4 |            6460.22 |                   117.932 |        1.18439e+07 |    1.13304e+07 |              357 |
| Proximal Policy Optimization        |                30 |               1536 |                             |                                  |                      366.917 |               61966.4 |             6235.2 |                   205.196 |        1.25242e+07 |    1.12337e+07 |             8200 |
| Tabu Search                         |                13 |                156 |                         407 |                                  |                      415.201 |               6099.14 |            5615.28 |                   313.212 |        1.53945e+07 |    1.09086e+07 |              210 |
| Proximal Policy Optimization Random |                17 |                595 |                             |                                  |                      407.522 |               32505.5 |            6478.39 |                   300.311 |        1.18351e+07 |    1.08675e+07 |             9840 |
| Simulated Annealing                 |                 6 |               1039 |                             |                               61 |                      431.474 |               26892.3 |            6000.73 |                   401.691 |        1.13937e+07 |    1.11507e+07 |              536 |
| Tabu Search Random                  |                 9 |                 26 |                           0 |                                  |                      405.941 |               45240.1 |            6152.13 |                   367.441 |        1.19013e+07 |    1.12509e+07 |               25 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search</th>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Consulta_Data_Mining_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                14 |               2491 |                             |                                  |                      354.015 |               15552.3 |            6711.04 |                   271.133 |        1.15323e+07 |    1.08673e+07 |             8630 |
| Tabu Search                         |                21 |               1443 |                        1374 |                                  |                      169.183 |               16326.9 |            6453.47 |                   107.354 |        1.14417e+07 |    1.09137e+07 |              508 |
| Tabu Search Random                  |                10 |                 29 |                           0 |                                  |                      402.302 |               17340.7 |            5849.89 |                   265.309 |        1.16251e+07 |    1.12549e+07 |               29 |
| Simulated Annealing                 |                19 |               1028 |                             |                             1435 |                      357.962 |               16897.4 |            5863.78 |                    228.51 |        1.17937e+07 |    1.13394e+07 |              538 |
| Simulated Annealing Random          |                21 |                755 |                             |                                0 |                      402.086 |               10307.5 |            6233.14 |                   77.2871 |        1.14658e+07 |    1.10758e+07 |              475 |
| Proximal Policy Optimization        |                27 |               2371 |                             |                                  |                      250.507 |               39678.4 |            6441.33 |                    161.69 |        1.18794e+07 |    1.12483e+07 |             8410 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Consulta_Data_Mining_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Consulta_Data_Mining_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Gov

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Gov_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Gov_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Gov_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Gov_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Gov_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Gov_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                 6 |                283 |                             |                                0 |                      26094.2 |               21950.9 |            16326.9 |                   20502.1 |        1.77299e+07 |    1.48118e+07 |              224 |
| Proximal Policy Optimization        |                19 |               1513 |                             |                                  |                      16202.4 |                114188 |            22581.1 |                   6818.76 |        2.29747e+07 |    1.65511e+07 |             2960 |
| Proximal Policy Optimization Random |                 8 |               1292 |                             |                                  |                      16627.8 |               38220.7 |              16503 |                   10819.3 |        1.97086e+07 |    1.66394e+07 |             2141 |
| Simulated Annealing                 |                13 |                380 |                             |                             5397 |                      22997.7 |               39174.3 |            15579.2 |                     12078 |        1.98933e+07 |    1.57884e+07 |              436 |
| Tabu Search                         |                16 |                279 |                           0 |                                  |                      21172.7 |               49389.3 |            15744.2 |                   11317.7 |        1.96246e+07 |    1.66557e+07 |              107 |
| Tabu Search Random                  |                 4 |                  9 |                           0 |                                  |                      31842.3 |                 50827 |            17978.8 |                   20743.8 |        1.63184e+07 |    1.44806e+07 |                9 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Gov_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Gov_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Gov_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Gov_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Gov_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Gov_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Gov_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                 5 |                260 |                             |                                0 |                      27205.9 |               17489.5 |            15362.9 |                   20141.6 |        1.68972e+07 |     1.4582e+07 |              208 |
| Simulated Annealing                 |                 4 |                  2 |                             |                               57 |                      26455.9 |               57958.7 |            16098.6 |                   22732.4 |         2.2491e+07 |    1.57653e+07 |                4 |
| Tabu Search                         |                 9 |                 21 |                           0 |                                  |                      26606.1 |               58379.5 |            17174.7 |                     16308 |         1.8935e+07 |    1.49147e+07 |               47 |
| Proximal Policy Optimization        |                 3 |               1002 |                             |                                  |                      32647.9 |               16824.2 |            16297.8 |                   30929.9 |        1.70208e+07 |    1.58872e+07 |             1005 |
| Tabu Search Random                  |                 6 |                 10 |                           0 |                                  |                      32359.8 |               24904.8 |            18364.8 |                     25940 |        1.86589e+07 |    1.57566e+07 |               12 |
| Proximal Policy Optimization Random |                 3 |                955 |                             |                                  |                      30572.2 |               18615.2 |            18202.9 |                   26730.4 |        2.02035e+07 |    1.72073e+07 |             1124 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Gov_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Gov_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Gov_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Gov_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Gov_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Gov_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Gov_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                14 |                261 |                             |                             5965 |                      20624.5 |                131950 |            16679.8 |                   9974.93 |        2.84575e+07 |    1.37349e+07 |              436 |
| Proximal Policy Optimization Random |                 4 |                  2 |                             |                                  |                      31570.7 |               29507.8 |              17416 |                   27229.8 |        2.06983e+07 |    1.87449e+07 |               40 |
| Tabu Search                         |                23 |                251 |                           0 |                                  |                      15466.1 |               79917.1 |            18424.2 |                   7523.86 |        1.33973e+07 |    1.05218e+07 |              263 |
| Tabu Search Random                  |                 9 |                 35 |                           0 |                                  |                      23175.2 |                277960 |            17099.1 |                   13762.5 |        3.18784e+07 |    1.67235e+07 |               39 |
| Simulated Annealing Random          |                13 |                329 |                             |                                0 |                      23271.2 |               63004.7 |            15398.1 |                   16524.7 |        2.25602e+07 |    1.55232e+07 |              245 |
| Proximal Policy Optimization        |                12 |                311 |                             |                                  |                      21161.4 |                427582 |            17853.6 |                   8724.54 |        5.06741e+07 |    1.63572e+07 |             1740 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Gov_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Gov_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Insurance

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Insurance_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Insurance_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Insurance_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Insurance_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Insurance_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Insurance_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                14 |                576 |                             |                                  |                      6945.97 |               10507.8 |        0.000125033 |                    4322.7 |        2.18484e+07 |    2.11148e+07 |             6380 |
| Simulated Annealing Random          |                42 |                609 |                             |                                0 |                      4733.08 |               16923.2 |        0.000117582 |                   1552.04 |        2.26663e+07 |    2.12654e+07 |              532 |
| Proximal Policy Optimization        |                34 |               2074 |                             |                                  |                      4433.41 |               18527.3 |        0.000116494 |                   3304.72 |        2.18687e+07 |    2.07091e+07 |             7040 |
| Simulated Annealing                 |                35 |                331 |                             |                              531 |                      8281.91 |               2091.42 |        0.000122913 |                   5444.12 |        2.20013e+07 |    2.09449e+07 |              675 |
| Tabu Search Random                  |                20 |                 96 |                           0 |                                  |                      7720.85 |               4222.09 |        0.000121963 |                   4110.18 |        2.20979e+07 |    2.15495e+07 |               90 |
| Tabu Search                         |                66 |                261 |                         539 |                                  |                      5203.88 |               7433.62 |        0.000123237 |                   3163.88 |        2.19604e+07 |    2.10721e+07 |              582 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
<th>Tabu Search</th>
</tr><tr>
<td><img src='report_images/Insurance_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Insurance_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Insurance_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Insurance_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Insurance_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Insurance_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Insurance_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                 6 |                388 |                             |                                  |                      9909.22 |               680.976 |         0.00011856 |                   9711.92 |        2.23003e+07 |    2.15172e+07 |             3269 |
| Tabu Search Random                  |                 2 |                  2 |                           0 |                                  |                      10545.1 |                1186.9 |        0.000121782 |                   10230.4 |         2.2355e+07 |    2.20561e+07 |                4 |
| Proximal Policy Optimization Random |                13 |                650 |                             |                                  |                      10051.4 |               589.183 |        0.000125266 |                   9646.19 |        2.22657e+07 |    2.18403e+07 |             7370 |
| Simulated Annealing                 |                 9 |                385 |                             |                               33 |                      9735.43 |               1230.37 |        0.000115974 |                   9530.31 |         2.1984e+07 |    2.12211e+07 |              693 |
| Simulated Annealing Random          |                 4 |                355 |                             |                                0 |                      10016.3 |                6295.8 |        0.000116415 |                   9839.26 |        2.21125e+07 |     2.1791e+07 |              236 |
| Tabu Search                         |                 9 |                117 |                        1117 |                                  |                      10013.2 |               416.181 |          0.0001184 |                   9595.67 |        2.21161e+07 |    2.17764e+07 |              257 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
</tr><tr>
<td><img src='report_images/Insurance_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Insurance_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Insurance_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Insurance_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Insurance_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Insurance_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Insurance_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                24 |                213 |                             |                                  |                       7829.7 |                 21629 |        0.000119552 |                   6503.66 |        2.25286e+07 |    2.12507e+07 |             5900 |
| Proximal Policy Optimization Random |                19 |                 81 |                             |                                  |                      8239.04 |               25732.6 |        0.000115148 |                   7403.33 |        2.24371e+07 |    2.12094e+07 |             2750 |
| Tabu Search                         |                24 |                250 |                         973 |                                  |                      9590.87 |               2333.37 |        0.000121475 |                   8446.93 |        2.21005e+07 |    2.12882e+07 |              521 |
| Tabu Search Random                  |                10 |                 56 |                           0 |                                  |                      9861.28 |               3118.35 |        0.000123739 |                   8049.84 |         2.2328e+07 |    2.15111e+07 |               59 |
| Simulated Annealing                 |                15 |                372 |                             |                              135 |                      9421.57 |               1397.23 |        0.000112675 |                   8374.64 |        2.19224e+07 |    2.14326e+07 |              691 |
| Simulated Annealing Random          |                15 |                389 |                             |                                0 |                      9130.72 |               20397.5 |        0.000113679 |                   6707.26 |        2.30258e+07 |    2.19076e+07 |              274 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Insurance_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Insurance_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Production

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Production_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Production_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Production_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Production_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Production_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Production_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                47 |               1613 |                        1150 |                                  |                      1866.25 |               99144.4 |            20775.8 |                      1275 |        4.21807e+07 |    4.08895e+07 |              470 |
| Tabu Search Random                  |                41 |                967 |                           0 |                                  |                      2511.28 |               43486.5 |            18300.3 |                   1817.65 |        4.22467e+07 |    4.05114e+07 |              790 |
| Proximal Policy Optimization Random |                45 |                715 |                             |                                  |                      1503.18 |                211330 |            19394.6 |                   1026.66 |        4.25095e+07 |    4.10983e+07 |             5417 |
| Proximal Policy Optimization        |                50 |                433 |                             |                                  |                      1393.31 |                158756 |            18884.9 |                   986.332 |        4.22143e+07 |     4.0297e+07 |             5190 |
| Simulated Annealing                 |                37 |                909 |                             |                             4850 |                      2657.53 |               39568.9 |            19465.7 |                   2089.03 |        4.24021e+07 |    4.12154e+07 |              510 |
| Simulated Annealing Random          |                35 |               1076 |                             |                               22 |                      2842.55 |               42094.1 |            17468.6 |                   1927.91 |        4.23852e+07 |      4.115e+07 |              868 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Production_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Production_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Production_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Production_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Production_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Production_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Production_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                18 |                421 |                        1607 |                                  |                         3357 |                222307 |            17827.8 |                   2958.22 |        4.27518e+07 |    4.12227e+07 |              349 |
| Simulated Annealing Random          |                 8 |                363 |                             |                                0 |                      3386.54 |                131318 |            19407.7 |                   2913.66 |        4.25681e+07 |    4.18752e+07 |              274 |
| Proximal Policy Optimization        |                 8 |                198 |                             |                                  |                      3395.28 |               57158.1 |            18236.2 |                   3312.91 |        4.26699e+07 |    4.14482e+07 |             6009 |
| Proximal Policy Optimization Random |                13 |                454 |                             |                                  |                      3488.99 |               20836.2 |            18591.7 |                   3324.69 |        4.27135e+07 |    4.15109e+07 |            10000 |
| Tabu Search Random                  |                 8 |                 38 |                           0 |                                  |                      3495.72 |                122346 |              18696 |                   3229.58 |        4.20802e+07 |    4.10975e+07 |               40 |
| Simulated Annealing                 |                12 |               1142 |                             |                              478 |                      3465.95 |                120724 |            18735.7 |                    3316.3 |          4.275e+07 |    4.14388e+07 |              478 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
</tr><tr>
<td><img src='report_images/Production_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Production_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Production_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Production_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Production_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Production_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Production_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization        |                42 |               2676 |                             |                                  |                      2699.64 |                244719 |            18567.7 |                   1979.87 |        4.27068e+07 |    4.09376e+07 |             8060 |
| Tabu Search Random                  |                15 |                107 |                           0 |                                  |                      3302.76 |               37616.6 |            17742.1 |                   3017.75 |        4.21376e+07 |    4.09571e+07 |               88 |
| Proximal Policy Optimization Random |                36 |               1528 |                             |                                  |                      2921.49 |                114675 |            18708.5 |                   2395.72 |        4.25273e+07 |     4.0404e+07 |             8760 |
| Simulated Annealing                 |                30 |               1185 |                             |                             4965 |                      3259.96 |                 42165 |            18347.8 |                   2650.36 |        4.21387e+07 |    4.06497e+07 |              533 |
| Simulated Annealing Random          |                17 |                494 |                             |                                0 |                      3222.15 |               52595.6 |            18420.6 |                   2864.07 |        4.25709e+07 |     4.1036e+07 |              353 |
| Tabu Search                         |                44 |               2104 |                        1121 |                                  |                       2929.1 |                140953 |            17745.8 |                    2425.2 |        4.27049e+07 |    4.08916e+07 |              528 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing</th>
<th>Simulated Annealing Random</th>
<th>Tabu Search</th>
</tr><tr>
<td><img src='report_images/Production_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Production_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Purchasing Example

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Purchasing_Example_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Purchasing_Example_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                66 |                100 |                        6024 |                                  |                       872.82 |               17087.1 |            13188.9 |                   449.941 |        3.49465e+07 |    3.32426e+07 |              460 |
| Simulated Annealing Random          |                36 |                555 |                             |                              106 |                       676.57 |               25119.4 |            13159.7 |                   480.777 |        3.55237e+07 |    3.36685e+07 |              468 |
| Simulated Annealing                 |                21 |                231 |                             |                              791 |                       1163.3 |               15749.5 |            12834.4 |                    545.17 |        3.54894e+07 |     3.4329e+07 |              493 |
| Tabu Search Random                  |                21 |                868 |                         395 |                                  |                       753.18 |               17761.9 |            13217.8 |                   556.669 |        3.54891e+07 |     3.4227e+07 |              700 |
| Proximal Policy Optimization Random |                56 |                  6 |                             |                                  |                      534.415 |                 34313 |            12989.7 |                   296.582 |        3.54005e+07 |    3.37608e+07 |             2330 |
| Proximal Policy Optimization        |                43 |                  8 |                             |                                  |                      449.076 |               43184.7 |            12928.8 |                    178.91 |        3.58564e+07 |    3.34401e+07 |             2430 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Purchasing_Example_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Purchasing_Example_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Purchasing_Example_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Tabu Search                         |                27 |                 19 |                         110 |                                  |                      1353.08 |               59550.4 |            13462.1 |                   1059.06 |         3.6573e+07 |    3.49784e+07 |               73 |
| Proximal Policy Optimization Random |                11 |                 18 |                             |                                  |                      1897.74 |               35265.2 |            13009.4 |                   1835.32 |        3.55581e+07 |    3.47432e+07 |             3100 |
| Tabu Search Random                  |                 7 |                 50 |                           0 |                                  |                      1173.42 |               64006.2 |            13314.2 |                   1073.52 |        3.65412e+07 |    3.47237e+07 |               52 |
| Simulated Annealing                 |                17 |                162 |                             |                             1696 |                      1912.72 |               29503.3 |            13370.9 |                   1031.09 |        3.60005e+07 |    3.39881e+07 |              338 |
| Proximal Policy Optimization        |                 9 |                 19 |                             |                                  |                      1928.49 |               16835.9 |            13001.1 |                   1912.79 |         3.5661e+07 |    3.48879e+07 |             2667 |
| Simulated Annealing Random          |                 5 |                541 |                             |                                0 |                       1883.9 |                 32361 |            12760.7 |                   1056.26 |        3.69597e+07 |    3.48729e+07 |              414 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing</th>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Purchasing_Example_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Purchasing_Example_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Purchasing_Example_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                33 |                 65 |                             |                                  |                       1290.2 |                 40902 |              13423 |                   642.461 |        3.66452e+07 |    3.46787e+07 |             3130 |
| Simulated Annealing Random          |                24 |                983 |                             |                               74 |                      1729.68 |               29967.1 |            12885.4 |                   762.261 |        3.55964e+07 |    3.42911e+07 |              738 |
| Proximal Policy Optimization        |                32 |                 17 |                             |                                  |                      1524.35 |                 30951 |            13183.3 |                   931.013 |        3.57782e+07 |    3.45443e+07 |             3130 |
| Simulated Annealing                 |                34 |                217 |                             |                             5387 |                      1022.85 |               30291.8 |            13257.9 |                   678.387 |         3.5673e+07 |    3.37916e+07 |              480 |
| Tabu Search Random                  |                15 |                 75 |                           0 |                                  |                      1077.34 |               30100.8 |            13229.1 |                   953.633 |        3.54491e+07 |    3.45946e+07 |               63 |
| Tabu Search                         |                61 |                124 |                        4583 |                                  |                      1322.55 |               21115.1 |            13124.3 |                   750.199 |        3.52817e+07 |    3.39773e+07 |              498 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Simulated Annealing</th>
<th>Tabu Search Random</th>
<th>Tabu Search</th>
</tr><tr>
<td><img src='report_images/Purchasing_Example_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Purchasing_Example_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Sepsis Das

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Sepsis_Das_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Sepsis_Das_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Proximal Policy Optimization Random |                 7 |                 18 |                             |                                  |                      20385.5 |                174318 |             156983 |                   18592.3 |        4.88577e+07 |    4.68795e+07 |             2849 |
| Proximal Policy Optimization        |                28 |                  7 |                             |                                  |                      6305.35 |                264172 |             155985 |                   4243.08 |        4.88522e+07 |    4.54373e+07 |             4830 |
| Tabu Search                         |                 4 |                  1 |                          30 |                                  |                      18726.6 |                125919 |             121739 |                     16216 |        4.93868e+07 |    4.81111e+07 |                5 |
| Tabu Search Random                  |                 9 |               1126 |                        1136 |                                  |                      11330.3 |                132134 |             121390 |                   8755.65 |        4.91912e+07 |    4.70545e+07 |              830 |
| Simulated Annealing Random          |                15 |               1180 |                             |                             1008 |                      10316.2 |                179386 |             128493 |                   4233.59 |         5.0022e+07 |    4.72417e+07 |              868 |
| Simulated Annealing                 |                 1 |                  1 |                             |                               69 |                      25537.3 |                169598 |             169598 |                   25537.3 |        4.98798e+07 |    4.98798e+07 |                4 |

#### Pareto Front Images

<table><tr>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Sepsis_Das_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Sepsis_Das_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Sepsis_Das_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                 3 |                  2 |                             |                              114 |                      47280.1 |           2.76164e+06 |        2.70343e+06 |                   46888.4 |        7.80104e+07 |    7.74798e+07 |                7 |
| Tabu Search Random                  |                 1 |                  1 |                           0 |                                  |                      47088.4 |           2.57387e+06 |        2.57387e+06 |                   47088.4 |        7.79835e+07 |    7.79835e+07 |                3 |
| Simulated Annealing Random          |                 8 |                926 |                             |                               36 |                      28487.4 |           2.51413e+06 |        1.89205e+06 |                   24292.6 |        1.16187e+08 |    9.51691e+07 |              740 |
| Proximal Policy Optimization Random |                 5 |                 15 |                             |                                  |                      46534.7 |           2.77533e+06 |        2.50461e+06 |                   45574.2 |        7.93788e+07 |    7.79051e+07 |             3865 |
| Tabu Search                         |                 5 |                  1 |                          20 |                                  |                      47587.6 |           2.93964e+06 |        2.81282e+06 |                   47010.3 |        8.00764e+07 |    7.80771e+07 |                6 |
| Proximal Policy Optimization        |                 3 |                  9 |                             |                                  |                      46371.6 |           2.66203e+06 |        2.47632e+06 |                   46275.4 |        8.00567e+07 |    7.97912e+07 |             2955 |

#### Pareto Front Images

<table><tr>
<th>Tabu Search Random</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
</tr><tr>
<td><img src='report_images/Sepsis_Das_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Hard_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Sepsis_Das_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Sepsis_Das_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing Random          |                 5 |               1045 |                             |                                0 |                      20186.4 |                899261 |             762744 |                   19442.4 |        1.00127e+08 |    9.36153e+07 |              798 |
| Simulated Annealing                 |                 1 |                  2 |                             |                              152 |                      43785.9 |           2.28339e+06 |        2.28339e+06 |                   43785.9 |         7.4814e+07 |     7.4814e+07 |                8 |
| Tabu Search                         |                 5 |                  1 |                          18 |                                  |                      38674.8 |           1.66835e+06 |        1.45137e+06 |                   35191.7 |        7.27851e+07 |    7.11963e+07 |                6 |
| Tabu Search Random                  |                 1 |                  4 |                           0 |                                  |                        40570 |            1.7456e+06 |         1.7456e+06 |                     40570 |        7.50737e+07 |    7.50737e+07 |                7 |
| Proximal Policy Optimization        |                10 |                 20 |                             |                                  |                      26432.2 |           1.12776e+06 |             926937 |                   21868.5 |        9.44429e+07 |     8.5317e+07 |             5217 |
| Proximal Policy Optimization Random |                10 |                 47 |                             |                                  |                      38062.6 |           2.53954e+06 |        1.75074e+06 |                   36154.1 |        7.47033e+07 |    7.14556e+07 |             5240 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing Random</th>
<th>Tabu Search Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
</tr><tr>
<td><img src='report_images/Sepsis_Das_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Sepsis_Das_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

## Trafic Das

### Easy

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Trafic_Das_Easy_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Trafic_Das_Easy_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                 7 |                427 |                             |                             2248 |                      138.144 |                254892 |             196662 |                   133.425 |        2.33455e+06 |    1.46994e+06 |              577 |
| Tabu Search                         |                 4 |                216 |                        3412 |                                  |                      114.903 |                256695 |             201887 |                   112.741 |        2.31422e+06 |    1.90354e+06 |              485 |
| Proximal Policy Optimization Random |                 8 |                414 |                             |                                  |                      27.4882 |               1525.28 |            923.534 |                   13.2331 |             832854 |        89304.5 |             6234 |
| Proximal Policy Optimization        |                 5 |                136 |                             |                                  |                      13.1275 |               34954.4 |            33847.5 |                     9.772 |        2.55899e+06 |         607541 |             4818 |
| Tabu Search Random                  |                 5 |               1405 |                         383 |                                  |                      65.2418 |                229093 |             172558 |                   58.5382 |        1.78164e+06 |         866616 |              868 |
| Simulated Annealing Random          |                 4 |               1327 |                             |                              243 |                      167.926 |                202008 |             152807 |                    65.501 |        2.59429e+06 |    1.73049e+06 |              868 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Proximal Policy Optimization Random</th>
<th>Proximal Policy Optimization</th>
<th>Tabu Search Random</th>
<th>Simulated Annealing Random</th>
</tr><tr>
<td><img src='report_images/Trafic_Das_Easy_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Easy_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Easy_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Easy_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Easy_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Easy_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Hard

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Trafic_Das_Hard_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Trafic_Das_Hard_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                 9 |                573 |                             |                              773 |                      489.081 |           1.14739e+06 |        1.03638e+06 |                   415.338 |        6.02035e+07 |    3.89093e+06 |              598 |
| Tabu Search                         |                 5 |                181 |                        1214 |                                  |                      500.202 |           1.17663e+06 |        1.08321e+06 |                   480.715 |        4.54628e+06 |    4.14764e+06 |              186 |
| Simulated Annealing Random          |                 4 |               1185 |                             |                              165 |                      162.396 |           1.49264e+06 |             424451 |                   17.0185 |        3.05005e+07 |    2.59431e+06 |              857 |
| Proximal Policy Optimization Random |                22 |                280 |                             |                                  |                      72.8084 |           1.88497e+06 |        1.23931e+06 |                    23.913 |        1.14576e+07 |    8.03874e+06 |             3820 |
| Proximal Policy Optimization        |                23 |                 44 |                             |                                  |                      151.831 |           1.81056e+06 |             968508 |                   30.3375 |        1.23984e+07 |    3.63188e+06 |             1590 |
| Tabu Search Random                  |                 6 |                600 |                           0 |                                  |                       145.09 |           1.18345e+06 |             461474 |                   124.361 |        5.49233e+07 |    2.94059e+06 |              426 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Trafic_Das_Hard_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Hard_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Hard_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Hard_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Hard_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

### Mid

#### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>New Base Solutions (Radius)</strong><br><img src='report_plots/Trafic_Das_Mid_tabu_solutions_left_in_radius.png' alt='New Base Solutions (Radius)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>New Base Solutions (Temperature)</strong><br><img src='report_plots/Trafic_Das_Mid_sa_solutions_left_for_temperature.png' alt='New Base Solutions (Temperature)' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_median_batch_processing_per_task.png' alt='Median Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Median Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_median_wt-idle_per_task.png' alt='Median Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Wait+Idle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_min_wt-idle_per_task.png' alt='Min Wait+Idle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Min Batch Processing Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_min_batch_processing_per_task.png' alt='Min Batch Processing Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td></tr>
<tr><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/><br><em>Solution = Step</em></td><td></td></tr>
</table>

#### Summary Table (Final Values)

| Agent                               | Pareto Front Size | Explored Solutions | New Base Solutions (Radius) | New Base Solutions (Temperature) | Median Batch Processing Time | Median Wait+Idle Time | Min Wait+Idle Time | Min Batch Processing Time | Average Cycle Time | Min Cycle Time | Iteration Number |
| :---------------------------------- | ----------------: | -----------------: | --------------------------: | -------------------------------: | ---------------------------: | --------------------: | -----------------: | ------------------------: | -----------------: | -------------: | ---------------: |
| Simulated Annealing                 |                 3 |                522 |                             |                             1045 |                      400.801 |                815555 |             805885 |                   347.011 |        4.66844e+06 |    4.15021e+06 |              573 |
| Tabu Search                         |                 6 |                229 |                        2118 |                                  |                      342.418 |                932627 |             747170 |                   322.015 |        1.15793e+07 |    5.70311e+06 |              276 |
| Simulated Annealing Random          |                 3 |               1160 |                             |                              119 |                       113.19 |                312769 |            58861.4 |                    79.491 |        6.54016e+06 |         520078 |              868 |
| Proximal Policy Optimization        |                17 |                170 |                             |                                  |                      86.8867 |                349657 |             270279 |                   39.9835 |        1.15895e+07 |    1.47119e+06 |             8010 |
| Proximal Policy Optimization Random |                16 |                146 |                             |                                  |                       75.249 |                425069 |             313482 |                   37.1275 |        3.52303e+06 |    1.29862e+06 |             7180 |
| Tabu Search Random                  |                15 |               1306 |                         723 |                                  |                      196.057 |                507079 |             354092 |                   156.822 |        1.55542e+07 |    1.47197e+06 |              868 |

#### Pareto Front Images

<table><tr>
<th>Simulated Annealing</th>
<th>Tabu Search</th>
<th>Simulated Annealing Random</th>
<th>Proximal Policy Optimization</th>
<th>Proximal Policy Optimization Random</th>
<th>Tabu Search Random</th>
</tr><tr>
<td><img src='report_images/Trafic_Das_Mid_Simulated_Annealing_pareto_front.png' alt='Pareto Front for Simulated Annealing' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Mid_Tabu_Search_pareto_front.png' alt='Pareto Front for Tabu Search' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Mid_Simulated_Annealing_Random_pareto_front.png' alt='Pareto Front for Simulated Annealing Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Mid_Proximal_Policy_Optimization_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Mid_Proximal_Policy_Optimization_Random_pareto_front.png' alt='Pareto Front for Proximal Policy Optimization Random' style='width:300px;height:200px;'/></td>
<td><img src='report_images/Trafic_Das_Mid_Tabu_Search_Random_pareto_front.png' alt='Pareto Front for Tabu Search Random' style='width:300px;height:200px;'/></td>
</tr></table>

---

# Installation & Basic Usage

### Installation

1. Create a fresh Python 3.10 virtual environment, e.g. with `conda create --name optimos-python python=3.10`
1. Install `poetry` on your system by following the [offical guide](https://python-poetry.org/docs/#installation). Make sure, poetry is **NOT** installed in the virtual environment.
1. Activate the environment, e.g. with `conda activate optimos-python`
1. Run `poetry install` in the root directory of this repository

### Standalone Usage

_For now there is no CLI interface for the optimizer, so you have to modify the `main.py` script to your needs_

1. Open `main.py` in your editor
1. Change the `timetable_path`, `constraints_path` and `bpmn_path` to your needs.
   - _If you need a basic set of constraints for your model, you can use the `create_constraints.py` script_
1. Run `python main.py` to start the optimizer, you will see the output and process in the console
1. _If you want to change settings like the number of iterations you can do so in the `main.py` script as well_
1. **LEGACY OPTIMOS SUPPORT**: If you want optimos_v2 to behave like the old optimos, you can set the `optimos_legacy_mode` setting to True. This will disable all batching optimizations.

### Usage within PIX (docker)

1. Install Docker and Docker-Compose, refer to the [official website](https://docs.docker.com/get-docker/) for installation instructions
2. Clone the [pix-portal](https://github.com/AutomatedProcessImprovement/pix-portal) repository (`git clone https://github.com/AutomatedProcessImprovement/pix-portal.git`)
3. Checkout the `integrate-optimos-v2` branch (`git checkout integrate-optimos-v2`)
4. Create the following secrets:
   - `frontend/pix-web-ui/.session.secret`
   - `backend/services/api-server/.superuser_email.secret`
   - `backend/services/api-server/.system_email.secret`
   - `backend/services/api-server/.superuser_password.secret`
   - `backend/services/api-server/.key.secret`
   - `backend/services/api-server/.system_password.secret`
   - _For local development/testing you can just fill them with example values, e.g. "secret" or "secret@secret.secret"._
   - Furthermore create the following files: `backend/workers/mail/.secret_gmail_username` & `backend/workers/mail/.secret_gmail_app_password`;
     Those are the credentials for the gmail account that sends out mails. The Password is a [gmail app password](https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237), not the actual password. If you don't want to send out mails, you still need to create the files, but can enter any value.
5. Create the following `.env` files:
   - `backend/workers/mail/.env`
   - `backend/workers/kronos/.env`
   - `backend/workers/simulation-prosimos/.env`
   - `backend/workers/bps-discovery-simod/.env`
   - `backend/workers/optimos/.env`
   - `backend/services/api-server/.env`
   - `backend/services/kronos/.env`
   - _You will find a `.env.example` file in each of the folders, you can copy those file and rename them to `.env`_
6. Run `docker compose up --build` in the root directory of the pix-portal repository. You may add the `-d` flag to run it in detached mode, so you can close the terminal afterwards.
7. _This will take some time_
8. Open your browser and go to `localhost:9999`. You can use the credentials from the `.superuser_email.secret` and `.superuser_password.secret` files to login.

### Usage within PIX (local + debugging)

1. Do all of the **Usage within PIX (docker)** steps above
2. Stop the docker-based optimos: `docker compose stop optimos`
3. Modify the `backend/workers/optimos/.env` file to use the local host instead of the docker container, you can rename `.env.example-local` to `.env` for that
4. Create a new Python 3.10 virtual environment (e.g. with `conda create --name optimos-python python=3.10`)
5. Activate the environment, e.g. with `conda activate optimos-python`
6. Navigate to the `backend/workers/optimos` folder in the pix repo
7. Install the dependencies with `poetry install`
8. Start the optimos worker with `python python optimos_worker/main.py`
9. **Alteratively**: Start the optimos worker with the vs code debugger by running the `Launch Optimos Worker` configuration (most likely you'll need to adjust the python binary used there, you can do that in the `.vscode/launch.json` file)

## Development

### Updating the Optimos Version used by PIX

_If you have pushed commits to the master, this change needs to be picked up by PIX, to do that do the following:_

1. Navigate to the folder `backend/workers/optimos` in the pix project
1. Update the `poetry.lock` file: `poetry lock`
1. Rebuild & restart the optimos container: `docker compose up -d --build optimos`

### Running Tests

To run the tests, run `pytest`. The tests should also automatically show up in the test explorer of your IDE. (For VSCode, you need to install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))

### Collecting Coverage

To collect coverage, run `pytest --cov --cov-report=lcov:lcov.info --cov-report=term`. You can display it e.g. with the vscode extension [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters).

## Docs

While the code should be documented in most places, you can find additional information on e.g. the architecture in the [docs folder](./docs/)

## Improvements over Legacy Optimos

- **Support to optimize Batching**
- Fully Typed
- Unit Tested (with ~90% coverage)
- Follows a Action-Store-Reducer pattern, similar to Flux
- Multi-Threaded at important parts, takes cpu core count of host machine into account
- Almost all public interfaces are documented
- Class-Based (Not a huge monolithic script)
- No throwaway file creation; Everything in memory
- Immutable Data Structures, so no change to the timetable is ever unexpected
