# Optimos V2

The next generation of [Optimos](https://github.com/AutomatedProcessImprovement/roptimus-prime). A Resource, Roster and Batching optimizer using Prosimos simulator.

# Evaluation

## Overview

This report includes data for the following **agents**, **models**, and **modes**. Click on a model to jump to its section.

### Agents

- Proximal Policy Optimization
- Proximal Policy Optimization Random
- Simulated Annealing
- Simulated Annealing Random
- Tabu Search
- Tabu Search Random

### Models

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

### Modes

- Easy
- Hard
- Mid

---

## Metrics Explanation

Below is an explanation of the metrics used in this report. Note that one simulation (or 'Solution') corresponds to one step on the x-axis.

<ul>
<li><strong>Pareto Front Size:</strong> Number of solutions in the current Pareto Front.</li>
<li><strong>Explored Solutions:</strong> Total number of solutions for which all neighbors have been explored.</li>
<li><strong>Potential New Base Solutions:</strong> Potential new base solution within a small error radius for Tabu Search or within the temperature radius for Simulated Annealing.</li>
<li><strong>Average Cycle Time:</strong> Average cycle time (from first enablement to the end of last activity) of all solutions in the current Pareto Front.</li>
<li><strong>Min Cycle Time:</strong> Minimum cycle time among all solutions in the current Pareto Front.</li>
<li><strong>Average Batch Size:</strong> Average number of tasks per batch (with a non batched task having a batch size of 1).</li>
<li><strong>Iteration Number:</strong> In one iteration, multiple mutations are performed. Depending on the agent, the solutions will be treated differently. Note that the number of solutions per iteration is not the same for all agents.</li>
<li><strong>Time per Step:</strong> Average wall time per simulation step computed from differences between consecutive steps.</li>
<li><strong>Total Optimization Time:</strong> Total wall clock time from the first to the last iteration (in minutes) </li>
</ul>

### Bpi Challenge 2012

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 58,00 | 46,00 | 38,00 |
| Reference Random  | 37,00 | 39,00 | 33,00 |
| Reference Optimos | 53,00 | 40,00 | 35,00 |
| SA                | 39,00 | 35,00 | 26,00 |
| Tabu Search       | 35,00 | 17,00 | 25,00 |
| PPO               | 46,00 | 41,00 | 22,00 |
| Tabu Random       | 8,00  | 15,00 | 16,00 |
| SA Random         | 26,00 | 20,00 | 18,00 |
| PPO Random        | 41,00 | 38,00 | 28,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,98 | 1,00 | 1,00 |
| Reference Optimos | 1,00 | 0,99 | 1,00 |
| SA                | 0,96 | 0,97 | 1,00 |
| Tabu Search       | 0,92 | 0,94 | 1,00 |
| PPO               | 1,00 | 0,99 | 1,00 |
| Tabu Random       | 0,68 | 0,95 | 1,00 |
| SA Random         | 0,86 | 0,95 | 1,00 |
| PPO Random        | 0,98 | 1,00 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid      | Hard      |
| ----------------- | --------- | -------- | --------- |
| Reference Random  | 9.987,18  | 3.703,22 | 3.415,36  |
| Reference Optimos | 272,36    | 5.523,63 | 10.161,03 |
| SA                | 15.408,62 | 5.939,53 | 29.585,14 |
| Tabu Search       | 9.883,80  | 6.427,54 | 29.616,95 |
| PPO               | 306,40    | 5.514,86 | 10.727,28 |
| Tabu Random       | 15.738,85 | 7.246,00 | 15.877,69 |
| SA Random         | 17.805,24 | 6.174,27 | 22.952,28 |
| PPO Random        | 9.989,72  | 3.703,29 | 11.101,33 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,99 | 1,25 | 1,23 |
| Reference Optimos | 1,66 | 1,15 | 1,16 |
| SA                | 1,03 | 1,04 | 1,04 |
| Tabu Search       | 1,03 | 1,16 | 1,01 |
| PPO               | 1,64 | 1,14 | 1,01 |
| Tabu Random       | 1,19 | 1,05 | 1,44 |
| SA Random         | 1,27 | 1,12 | 1,03 |
| PPO Random        | 1,00 | 1,25 | 1,13 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,28 | 0,46 | 0,37 |
| Reference Optimos | 0,72 | 0,54 | 0,63 |
| SA                | 0,19 | 0,24 | 0,24 |
| Tabu Search       | 0,17 | 0,09 | 0,34 |
| PPO               | 0,33 | 0,22 | 0,05 |
| Tabu Random       | 0,00 | 0,00 | 0,11 |
| SA Random         | 0,00 | 0,00 | 0,08 |
| PPO Random        | 0,26 | 0,46 | 0,18 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy         | Mid          | Hard         |
| ----------------- | ------------ | ------------ | ------------ |
| Base              | 1.218.264,58 | 1.218.354,45 | 1.218.264,60 |
| Reference         | 1.231.617,45 | 1.393.767,17 | 2.425.820,43 |
| Reference Random  | 1.212.931,15 | 1.436.835,71 | 3.367.277,38 |
| Reference Optimos | 1.233.554,65 | 1.435.539,34 | 5.363.983,24 |
| SA                | 1.304.858,77 | 1.369.175,11 | 1.426.754,04 |
| Tabu Search       | 1.228.740,83 | 1.356.749,39 | 1.568.009,15 |
| PPO               | 1.221.187,53 | 1.431.114,38 | 6.589.850,99 |
| Tabu Random       | 1.259.535,84 | 1.370.966,56 | 1.784.573,13 |
| SA Random         | 1.353.113,82 | 1.371.905,30 | 1.606.825,51 |
| PPO Random        | 1.212.012,24 | 1.433.278,06 | 4.959.761,62 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy         | Mid          | Hard         |
| ----------------- | ------------ | ------------ | ------------ |
| Base              | 1.218.264,58 | 1.218.354,45 | 1.218.264,60 |
| Reference         | 1.166.893,73 | 1.170.000,00 | 1.166.304,58 |
| Reference Random  | 1.163.321,38 | 1.170.000,00 | 1.166.304,58 |
| Reference Optimos | 1.163.504,07 | 1.210.386,51 | 1.170.135,16 |
| SA                | 1.209.128,12 | 1.213.770,44 | 1.210.526,41 |
| Tabu Search       | 1.211.702,72 | 1.213.581,21 | 1.217.329,58 |
| PPO               | 1.163.504,07 | 1.170.003,63 | 1.170.000,00 |
| Tabu Random       | 1.170.000,00 | 1.170.000,00 | 1.211.329,39 |
| SA Random         | 1.170.000,00 | 1.170.000,00 | 1.211.040,39 |
| PPO Random        | 1.163.321,38 | 1.170.000,00 | 1.166.304,58 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2012_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  9991 |               1020 |                              |        1.22262e+06 |     1.1635e+06 |            17.8497 |            10000 |       4.33396 | 549min<br/>(for 9991 Steps) |
| Proximal Policy Optimization Random |  9991 |               1347 |                              |        1.21544e+06 |    1.16689e+06 |            2.54891 |            10000 |       3.13432 | 383min<br/>(for 9991 Steps) |
| Simulated Annealing                 |  9993 |                454 |                           27 |        1.30261e+06 |    1.20913e+06 |            5.92322 |              602 |       3.59493 | 76min<br/>(for 9993 Steps)  |
| Simulated Annealing Random          |   915 |                459 |                            0 |         1.3469e+06 |    1.21027e+06 |            4.44316 |              307 |       1.45809 | 24min<br/>(for 915 Steps)   |
| Tabu Search                         |  6922 |                559 |                            0 |        1.23741e+06 |     1.2117e+06 |            5.03646 |              390 |       3.05839 | 43min<br/>(for 6922 Steps)  |
| Tabu Search Random                  |    60 |                 35 |                            0 |        1.27674e+06 |    1.21298e+06 |                  2 |               22 |       1.56687 | 1min<br/>(for 60 Steps)     |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2012_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  9991 |               1748 |                              |        7.74888e+06 |    1.17014e+06 |                  2 |            10000 |       2.76076 | 486min<br/>(for 9991 Steps) |
| Proximal Policy Optimization Random |  9991 |               1209 |                              |        4.82441e+06 |     1.1663e+06 |                  2 |            10000 |       5.43813 | 644min<br/>(for 9991 Steps) |
| Simulated Annealing                 |  8534 |                456 |                            0 |        1.41545e+06 |    1.21131e+06 |            5.39286 |              565 |      0.252189 | 91min<br/>(for 8534 Steps)  |
| Simulated Annealing Random          |   720 |                354 |                            0 |        1.58524e+06 |    1.21104e+06 |                  0 |              242 |       1.85308 | 20min<br/>(for 720 Steps)   |
| Tabu Search                         |  2933 |                297 |                            0 |        1.52894e+06 |    1.21731e+06 |            16.5698 |              168 |      0.572584 | 27min<br/>(for 2933 Steps)  |
| Tabu Search Random                  |   180 |                 65 |                            0 |         1.7864e+06 |    1.21133e+06 |                  0 |               62 |       1.41545 | 5min<br/>(for 180 Steps)    |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2012_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  9991 |               1754 |                              |        1.42909e+06 |       1.17e+06 |            5.55513 |            10000 |       2.50255 | 429min<br/>(for 9991 Steps) |
| Proximal Policy Optimization Random |  9991 |               1677 |                              |        1.46688e+06 |       1.17e+06 |            2.97665 |            10000 |       2.94587 | 471min<br/>(for 9991 Steps) |
| Simulated Annealing                 | 10006 |                696 |                            9 |        1.37587e+06 |    1.21377e+06 |                  2 |              642 |      0.275636 | 71min<br/>(for 10006 Steps) |
| Simulated Annealing Random          |   759 |                429 |                            0 |        1.39163e+06 |    1.21732e+06 |                  2 |              255 |        1.0461 | 18min<br/>(for 759 Steps)   |
| Tabu Search                         |  2496 |                146 |                            0 |        1.36132e+06 |    1.21358e+06 |            2.63385 |              133 |      0.264846 | 16min<br/>(for 2496 Steps)  |
| Tabu Search Random                  |   129 |                 50 |                            0 |        1.38085e+06 |    1.21129e+06 |            43.3714 |               45 |       1.22801 | 3min<br/>(for 129 Steps)    |

##### Pareto Front Images

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

---

### Bpi Challenge 2017

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 68,00 | 34,00 | 22,00 |
| Reference Random  | 46,00 | 31,00 | 9,00  |
| Reference Optimos | 59,00 | 35,00 | 21,00 |
| SA                | 34,00 | 26,00 | 25,00 |
| Tabu Search       | 39,00 | 36,00 | 2,00  |
| PPO               | 40,00 | 32,00 | 16,00 |
| Tabu Random       | 19,00 | 11,00 | 4,00  |
| SA Random         | 19,00 | 21,00 | 7,00  |
| PPO Random        | 33,00 | 32,00 | 12,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 0,96 | 1,00 |
| Reference Optimos | 1,00 | 1,00 | 1,00 |
| SA                | 0,81 | 0,93 | 1,00 |
| Tabu Search       | 0,95 | 0,98 | 1,00 |
| PPO               | 1,00 | 0,99 | 1,00 |
| Tabu Random       | 0,85 | 0,86 | 1,00 |
| SA Random         | 0,86 | 0,91 | 1,00 |
| PPO Random        | 1,00 | 0,95 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid       | Hard       |
| ----------------- | --------- | --------- | ---------- |
| Reference Random  | 79,08     | 21.159,01 | 7.660,72   |
| Reference Optimos | 4.916,98  | 442,87    | 1.114,51   |
| SA                | 13.998,34 | 3.563,03  | 764,08     |
| Tabu Search       | 959,61    | 7.012,05  | 21.714,03  |
| PPO               | 5.836,54  | 2.629,91  | 118.980,27 |
| Tabu Random       | 10.561,28 | 4.241,19  | 14.593,91  |
| SA Random         | 2.472,96  | 20.629,72 | 7.716,23   |
| PPO Random        | 152,81    | 8.273,79  | 24.916,06  |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,07 | 1,33 | 1,43 |
| Reference Optimos | 1,36 | 1,27 | 0,95 |
| SA                | 1,30 | 1,03 | 1,06 |
| Tabu Search       | 0,89 | 1,12 | 1,00 |
| PPO               | 1,34 | 1,29 | 0,96 |
| Tabu Random       | 1,16 | 1,22 | 0,80 |
| SA Random         | 1,38 | 1,09 | 1,36 |
| PPO Random        | 1,03 | 1,07 | 1,01 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,31 | 0,26 | 0,18 |
| Reference Optimos | 0,69 | 0,74 | 0,82 |
| SA                | 0,29 | 0,21 | 0,68 |
| Tabu Search       | 0,34 | 0,26 | 0,00 |
| PPO               | 0,10 | 0,26 | 0,14 |
| Tabu Random       | 0,01 | 0,00 | 0,00 |
| SA Random         | 0,06 | 0,00 | 0,14 |
| PPO Random        | 0,26 | 0,26 | 0,05 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy       | Mid          | Hard          |
| ----------------- | ---------- | ------------ | ------------- |
| Base              | 852.467,43 | 852.710,18   | 852.702,68    |
| Reference         | 839.940,98 | 990.747,76   | 991.046,77    |
| Reference Random  | 846.410,93 | 966.070,75   | 996.937,34    |
| Reference Optimos | 842.130,74 | 988.114,18   | 985.012,14    |
| SA                | 941.847,55 | 951.636,32   | 964.062,54    |
| Tabu Search       | 861.506,82 | 920.061,23   | 4.712.685,16  |
| PPO               | 852.272,83 | 1.060.722,98 | 17.301.316,04 |
| Tabu Random       | 894.732,99 | 1.100.928,34 | 914.196,55    |
| SA Random         | 868.914,85 | 1.143.350,67 | 1.044.067,34  |
| PPO Random        | 844.653,56 | 926.197,95   | 15.219.855,60 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy       | Mid        | Hard       |
| ----------------- | ---------- | ---------- | ---------- |
| Base              | 852.467,43 | 852.710,18 | 852.702,68 |
| Reference         | 696.456,31 | 840.352,05 | 837.243,10 |
| Reference Random  | 773.072,94 | 838.151,30 | 837.243,10 |
| Reference Optimos | 622.341,70 | 840.352,05 | 838.174,03 |
| SA                | 847.721,61 | 846.218,83 | 845.162,58 |
| Tabu Search       | 696.456,31 | 846.408,80 | 852.516,38 |
| PPO               | 622.341,70 | 825.269,43 | 838.174,03 |
| Tabu Random       | 851.317,68 | 852.455,13 | 849.882,17 |
| SA Random         | 850.046,38 | 848.571,22 | 851.497,36 |
| PPO Random        | 773.072,94 | 833.972,70 | 837.243,10 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2017_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  9991 |               2296 |                              |             851855 |         622342 |                  2 |            10000 |        4.0034 | 641min<br/>(for 9991 Steps)  |
| Proximal Policy Optimization Random |  9991 |               3480 |                              |             846913 |         773073 |            9.13759 |            10000 |       4.41904 | 579min<br/>(for 9991 Steps)  |
| Simulated Annealing                 |  9998 |               1495 |                          564 |             941853 |         847722 |                  2 |              655 |      0.717846 | 90min<br/>(for 9998 Steps)   |
| Simulated Annealing Random          |  1190 |                641 |                            0 |             869780 |         850046 |            2.01457 |              398 |        2.4041 | 44min<br/>(for 1190 Steps)   |
| Tabu Search                         | 10000 |               2778 |                          829 |             878877 |         696456 |            5.55401 |              548 |       1.09289 | 103min<br/>(for 10000 Steps) |
| Tabu Search Random                  |   620 |                285 |                            0 |             899299 |         851318 |            2.19473 |              208 |       2.49187 | 25min<br/>(for 620 Steps)    |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2017_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  6299 |                734 |                              |         1.9778e+07 |         838174 |                  2 |             6309 |       2.62878 | 367min<br/>(for 6299 Steps) |
| Proximal Policy Optimization Random |  5489 |                649 |                              |        1.71763e+07 |         837243 |                  2 |             5499 |        3.2475 | 343min<br/>(for 5489 Steps) |
| Simulated Annealing                 |  9994 |               2069 |                          211 |             974249 |         845163 |                  2 |              698 |       1.04918 | 135min<br/>(for 9994 Steps) |
| Simulated Annealing Random          |   896 |                494 |                            0 |        1.04407e+06 |         851497 |                  2 |              300 |         2.024 | 32min<br/>(for 896 Steps)   |
| Tabu Search                         |    23 |                  5 |                            1 |             853221 |         852804 |                  0 |                4 |      0.012678 | 0min<br/>(for 23 Steps)     |
| Tabu Search Random                  |    26 |                 13 |                            0 |             884157 |         852467 |                  0 |               10 |        1.5919 | 1min<br/>(for 26 Steps)     |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpi_Challenge_2017_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  9991 |               1505 |                              |        1.02846e+06 |         825269 |                  2 |            10000 |       3.34574 | 518min<br/>(for 9991 Steps)  |
| Proximal Policy Optimization Random |  9095 |               1668 |                              |             933243 |         838151 |                  2 |             9105 |       3.33356 | 493min<br/>(for 9095 Steps)  |
| Simulated Annealing                 | 10000 |                835 |                          115 |             955819 |         846219 |                  0 |              684 |      0.568655 | 106min<br/>(for 10000 Steps) |
| Simulated Annealing Random          |   947 |                511 |                            0 |        1.11572e+06 |         850648 |                  2 |              317 |       2.13876 | 34min<br/>(for 947 Steps)    |
| Tabu Search                         | 10007 |               1426 |                          563 |             924136 |         846409 |            2.88612 |              599 |      0.756378 | 105min<br/>(for 10007 Steps) |
| Tabu Search Random                  |   173 |                 85 |                            0 |        1.12352e+06 |         852813 |             2.0259 |               59 |      0.090271 | 6min<br/>(for 173 Steps)     |

##### Pareto Front Images

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

---

### Bpic2019 Das

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 22,00 | 23,00 | 12,00 |
| Reference Random  | 19,00 | 16,00 | 12,00 |
| Reference Optimos | 15,00 | 23,00 | 9,00  |
| SA                | 6,00  | 7,00  | 12,00 |
| Tabu Search       | 2,00  | 8,00  | 20,00 |
| PPO               | 19,00 | 23,00 | 3,00  |
| Tabu Random       | 1,00  | 1,00  | 5,00  |
| SA Random         | 8,00  | 9,00  | 2,00  |
| PPO Random        | 21,00 | 19,00 | 11,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 1,00 | 1,00 |
| Reference Optimos | 1,00 | 1,00 | 1,00 |
| SA                | 0,98 | 0,96 | 1,00 |
| Tabu Search       | 0,99 | 0,97 | 1,00 |
| PPO               | 1,00 | 1,00 | 1,00 |
| Tabu Random       | 0,99 | 0,96 | 1,00 |
| SA Random         | 0,99 | 0,99 | 1,00 |
| PPO Random        | 1,00 | 1,00 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid        | Hard         |
| ----------------- | --------- | ---------- | ------------ |
| Reference Random  | 436,47    | 430.414,11 | 10.221,63    |
| Reference Optimos | 6.464,99  | 0,00       | 1.914.144,46 |
| SA                | 30.437,76 | 19.742,85  | 1.916.109,07 |
| Tabu Search       | 36.522,19 | 24.172,94  | 1.913.213,38 |
| PPO               | 7.252,59  | 0,00       | 1.912.100,68 |
| Tabu Random       | 36.850,45 | 22.667,19  | 1.913.565,79 |
| SA Random         | 20.186,07 | 545.936,82 | 1.916.106,86 |
| PPO Random        | 7.483,51  | 405.545,77 | 10.221,63    |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,78 | 1,11 | 1,62 |
| Reference Optimos | 1,18 | 1,03 | 1,00 |
| SA                | 0,96 | 0,96 | 1,00 |
| Tabu Search       | 0,96 | 0,98 | 1,00 |
| PPO               | 1,07 | 1,03 | 1,00 |
| Tabu Random       | 0,00 | 0,00 | 1,00 |
| SA Random         | 1,08 | 1,33 | 1,00 |
| PPO Random        | 0,90 | 1,12 | 1,62 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,86 | 0,00 | 0,67 |
| Reference Optimos | 0,14 | 1,00 | 0,33 |
| SA                | 0,00 | 0,00 | 0,17 |
| Tabu Search       | 0,05 | 0,00 | 0,08 |
| PPO               | 0,09 | 1,00 | 0,33 |
| Tabu Random       | 0,05 | 0,00 | 0,17 |
| SA Random         | 0,14 | 0,00 | 0,08 |
| PPO Random        | 0,68 | 0,00 | 0,67 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid            | Hard           |
| ----------------- | ------------- | -------------- | -------------- |
| Base              | 1.043.060,17  | 1.000.680,00   | 991.869,54     |
| Reference         | 13.254.654,93 | 8.620.197,31   | 657.315.714,08 |
| Reference Random  | 13.562.132,10 | 195.531.623,76 | 653.567.931,48 |
| Reference Optimos | 14.429.898,92 | 8.620.197,31   | 7.864.354,84   |
| SA                | 1.507.097,88  | 1.956.373,35   | 1.413.361,82   |
| Tabu Search       | 1.589.905,74  | 4.418.830,87   | 2.659.125,33   |
| PPO               | 11.638.988,73 | 8.620.197,31   | 15.876.716,15  |
| Tabu Random       | 1.746.895,25  | 2.076.818,41   | 1.044.893,23   |
| SA Random         | 2.499.499,15  | 199.021.926,37 | 4.707.934,03   |
| PPO Random        | 12.219.507,07 | 179.178.011,59 | 653.567.931,48 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy         | Mid          | Hard         |
| ----------------- | ------------ | ------------ | ------------ |
| Base              | 1.043.060,17 | 1.000.680,00 | 991.869,54   |
| Reference         | 1.067.163,66 | 3.005.361,94 | 925.020,00   |
| Reference Random  | 1.067.163,66 | 2.048.507,77 | 925.020,00   |
| Reference Optimos | 1.371.193,29 | 3.005.361,94 | 1.000.620,00 |
| SA                | 1.063.109,41 | 1.544.374,98 | 925.020,00   |
| Tabu Search       | 1.371.193,29 | 3.042.646,84 | 925.020,00   |
| PPO               | 1.082.014,13 | 3.005.361,94 | 925.020,00   |
| Tabu Random       | 1.746.895,25 | 2.076.818,41 | 925.020,00   |
| SA Random         | 1.067.163,66 | 2.048.507,77 | 925.020,00   |
| PPO Random        | 1.690.399,18 | 2.151.928,20 | 925.020,00   |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpic2019_Das_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpic2019_Das_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpic2019_Das_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time       |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :---------------------------- |
| Proximal Policy Optimization        |  2009 |                  2 |                              |         1.1639e+07 |    1.08201e+06 |            4.03617 |             2019 |        15.139 | 501min<br/>(for 2009 Steps)   |
| Proximal Policy Optimization Random |  4067 |                  2 |                              |        1.22195e+07 |     1.6904e+06 |            6.67055 |             4077 |        20.129 | 1,043min<br/>(for 4067 Steps) |
| Simulated Annealing                 |  9999 |                202 |                          938 |         1.5071e+06 |    1.06311e+06 |            2.78258 |              591 |       0.95725 | 419min<br/>(for 9999 Steps)   |
| Simulated Annealing Random          |  2633 |               1077 |                           20 |         2.4995e+06 |    1.06716e+06 |            3.92252 |              868 |       1.46477 | 454min<br/>(for 2633 Steps)   |
| Tabu Search                         |  3537 |                 38 |                         1255 |        1.58991e+06 |    1.37119e+06 |            3.50991 |              176 |       2.03933 | 137min<br/>(for 3537 Steps)   |
| Tabu Search Random                  |   473 |                153 |                            0 |         1.7469e+06 |     1.7469e+06 |            5.83961 |              155 |       2.20628 | 62min<br/>(for 473 Steps)     |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpic2019_Das_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpic2019_Das_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpic2019_Das_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |   631 |                  8 |                              |        2.08606e+07 |    5.14389e+06 |            9.35763 |              640 |       111.327 | 773min<br/>(for 631 Steps)   |
| Proximal Policy Optimization Random |   771 |                  2 |                              |        1.97393e+09 |    3.22863e+06 |            9.58205 |              780 |       127.342 | 1,760min<br/>(for 771 Steps) |
| Simulated Annealing                 |  9270 |                193 |                         1695 |        2.19567e+06 |    1.00062e+06 |            3.10955 |              502 |      0.382867 | 358min<br/>(for 9270 Steps)  |
| Simulated Annealing Random          |   705 |                297 |                            0 |        6.59939e+06 |    3.35898e+06 |                  5 |              254 |       6.81138 | 314min<br/>(for 705 Steps)   |
| Tabu Search                         |  7986 |                161 |                         1055 |        3.98648e+06 |    1.42871e+06 |            3.54196 |              425 |       1.25507 | 333min<br/>(for 7986 Steps)  |
| Tabu Search Random                  |   128 |                 34 |                            0 |        2.48004e+06 |    1.00068e+06 |            3.72706 |               40 |       9.28795 | 25min<br/>(for 128 Steps)    |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Bpic2019_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Bpic2019_Das_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Bpic2019_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Bpic2019_Das_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Bpic2019_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Bpic2019_Das_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time       |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :---------------------------- |
| Proximal Policy Optimization        |   241 |                  1 |                              |        2.89777e+08 |    3.21102e+06 |            8.79699 |              250 |       44.0296 | 196min<br/>(for 241 Steps)    |
| Proximal Policy Optimization Random |  2541 |                  1 |                              |        1.79178e+08 |    2.15193e+06 |            5.65822 |             2550 |       20.6542 | 1,436min<br/>(for 2541 Steps) |
| Simulated Annealing                 | 10001 |                200 |                         2726 |        1.95637e+06 |    1.54438e+06 |            2.70882 |              593 |      0.388852 | 401min<br/>(for 10001 Steps)  |
| Simulated Annealing Random          |  1049 |                423 |                            0 |        1.77198e+08 |    2.04851e+06 |             4.1509 |              347 |       5.50982 | 225min<br/>(for 1049 Steps)   |
| Tabu Search                         |  6357 |                 96 |                          280 |        4.26219e+06 |    3.04265e+06 |            3.03069 |              346 |       1.85831 | 262min<br/>(for 6357 Steps)   |
| Tabu Search Random                  |    29 |                  5 |                            0 |        2.07682e+06 |    2.07682e+06 |            2.96169 |                7 |       7.34266 | 2min<br/>(for 29 Steps)       |

##### Pareto Front Images

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

---

### Callcentre

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 15,00 | 14,00 | 13,00 |
| Reference Random  | 9,00  | 17,00 | 17,00 |
| Reference Optimos | 15,00 | 5,00  | 9,00  |
| SA                | 7,00  | 4,00  | 5,00  |
| Tabu Search       | 1,00  | 4,00  | 1,00  |
| PPO               | 17,00 | 5,00  | 9,00  |
| Tabu Random       | 9,00  | 2,00  | 3,00  |
| SA Random         | 11,00 | 9,00  | 15,00 |
| PPO Random        | 9,00  | 12,00 | 8,00  |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 1,00 | 1,00 |
| Reference Optimos | 1,00 | 1,00 | 1,00 |
| SA                | 0,98 | 0,91 | 1,00 |
| Tabu Search       | 0,98 | 0,91 | 1,00 |
| PPO               | 1,00 | 1,00 | 1,00 |
| Tabu Random       | 0,99 | 0,84 | 1,00 |
| SA Random         | 1,00 | 1,00 | 1,00 |
| PPO Random        | 1,00 | 1,00 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid        | Hard       |
| ----------------- | --------- | ---------- | ---------- |
| Reference Random  | 20.522,85 | 1.199,31   | 17.646,90  |
| Reference Optimos | 0,00      | 26.800,08  | 3.270,60   |
| SA                | 33.019,80 | 271.567,49 | 517.182,71 |
| Tabu Search       | 29.609,43 | 216.393,82 | 581.762,66 |
| PPO               | 0,00      | 26.800,08  | 3.270,60   |
| Tabu Random       | 24.933,62 | 409.015,90 | 891.974,32 |
| SA Random         | 54.507,65 | 2.173,16   | 18.693,25  |
| PPO Random        | 20.522,85 | 17.516,95  | 13.509,85  |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,99 | 1,21 | 1,23 |
| Reference Optimos | 1,74 | 1,00 | 1,60 |
| SA                | 0,93 | 0,95 | 0,00 |
| Tabu Search       | 0,00 | 0,94 | 0,00 |
| PPO               | 1,74 | 1,00 | 1,60 |
| Tabu Random       | 1,02 | 0,97 | 0,92 |
| SA Random         | 1,29 | 1,01 | 1,19 |
| PPO Random        | 0,99 | 0,97 | 1,01 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,00 | 0,64 | 0,62 |
| Reference Optimos | 1,00 | 0,36 | 0,38 |
| SA                | 0,00 | 0,00 | 0,00 |
| Tabu Search       | 0,00 | 0,00 | 0,00 |
| PPO               | 1,00 | 0,36 | 0,38 |
| Tabu Random       | 0,00 | 0,00 | 0,00 |
| SA Random         | 0,00 | 0,21 | 0,62 |
| PPO Random        | 0,00 | 0,43 | 0,00 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 11.106.584,79 | 10.889.027,63 | 11.738.570,26 |
| Reference         | 71.718,79     | 114.388,32    | 83.654,70     |
| Reference Random  | 14.570,07     | 108.691,65    | 143.569,65    |
| Reference Optimos | 71.718,79     | 6.096,85      | 49.050,92     |
| SA                | 1.738.604,64  | 7.956.488,84  | 9.698.842,92  |
| Tabu Search       | 1.527.949,36  | 9.167.885,21  | 10.225.921,16 |
| PPO               | 71.718,79     | 6.096,85      | 49.050,92     |
| Tabu Random       | 1.146.321,93  | 9.011.205,66  | 19.606.665,88 |
| SA Random         | 15.340.975,24 | 191.474,45    | 172.392,03    |
| PPO Random        | 14.570,07     | 79.599,66     | 15.676,56     |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 11.106.584,79 | 10.889.027,63 | 11.738.570,26 |
| Reference         | 1.881,05      | 5.758,89      | 4.876,96      |
| Reference Random  | 1.902,42      | 4.281,56      | 4.876,96      |
| Reference Optimos | 1.881,05      | 5.758,89      | 4.417,33      |
| SA                | 1.387.596,57  | 7.093.163,15  | 9.698.842,92  |
| Tabu Search       | 1.527.949,36  | 8.719.642,93  | 10.225.921,16 |
| PPO               | 1.881,05      | 5.758,89      | 4.417,33      |
| Tabu Random       | 1.066.232,87  | 8.773.247,05  | 10.438.156,55 |
| SA Random         | 191.679,36    | 4.281,56      | 4.876,96      |
| PPO Random        | 1.902,42      | 34.311,62     | 4.562,45      |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Callcentre_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Callcentre_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Callcentre_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  6600 |                405 |                              |            73793.5 |        1881.05 |            25.3167 |             6610 |       3.35217 | 361min<br/>(for 6600 Steps) |
| Proximal Policy Optimization Random |  5241 |                326 |                              |            12413.4 |        1951.83 |            4.70833 |             5250 |       9.54398 | 717min<br/>(for 5241 Steps) |
| Simulated Annealing                 | 10002 |                360 |                         1088 |         1.7386e+06 |     1.3876e+06 |            2.54301 |              664 |      0.907438 | 82min<br/>(for 10002 Steps) |
| Simulated Annealing Random          |  2600 |               1314 |                          542 |         1.5341e+07 |         191679 |            3.18854 |              868 |         2.347 | 104min<br/>(for 2600 Steps) |
| Tabu Search                         |   305 |                  4 |                            0 |        1.52795e+06 |    1.52795e+06 |            2.27386 |               21 |       1.54933 | 2min<br/>(for 305 Steps)    |
| Tabu Search Random                  |  2600 |               1536 |                          356 |        1.19836e+06 |    1.06623e+06 |            2.60242 |              868 |       1.45499 | 88min<br/>(for 2600 Steps)  |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Callcentre_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Callcentre_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Callcentre_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  3511 |                349 |                              |            45649.9 |        4417.33 |            26.3333 |             3520 |        17.117 | 716min<br/>(for 3511 Steps) |
| Proximal Policy Optimization Random |  4347 |                590 |                              |            15676.6 |        4562.45 |            26.1556 |             4357 |       14.0817 | 601min<br/>(for 4347 Steps) |
| Simulated Annealing                 |  7152 |                311 |                            0 |        1.02421e+07 |    9.80554e+06 |            5.39037 |              468 |      0.367432 | 45min<br/>(for 7152 Steps)  |
| Simulated Annealing Random          |  2600 |               1339 |                          655 |             172392 |        4876.96 |            7.15138 |              868 |       3.11103 | 107min<br/>(for 2600 Steps) |
| Tabu Search                         |   103 |                  4 |                            0 |        1.02259e+07 |    1.02259e+07 |            3.53407 |                9 |       2.63266 | 0min<br/>(for 103 Steps)    |
| Tabu Search Random                  |    47 |                 16 |                            0 |        1.98113e+07 |    1.10522e+07 |            3.45809 |               18 |       2.05723 | 1min<br/>(for 47 Steps)     |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Callcentre_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Callcentre_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Callcentre_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Callcentre_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Callcentre_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Callcentre_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Callcentre_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Callcentre_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  2106 |                 84 |                              |            6096.85 |        5758.89 |            2.72419 |             2116 |       3.47716 | 140min<br/>(for 2106 Steps) |
| Proximal Policy Optimization Random |  8994 |                494 |                              |            80850.5 |        34311.6 |            8.81466 |             9004 |       4.83608 | 699min<br/>(for 8994 Steps) |
| Simulated Annealing                 | 10011 |                389 |                           52 |        7.95649e+06 |    7.09316e+06 |            2.88614 |              668 |   0.000984311 | 78min<br/>(for 10011 Steps) |
| Simulated Annealing Random          |  2600 |               1290 |                          671 |             191474 |        4281.56 |            10.7397 |              868 |       2.08443 | 98min<br/>(for 2600 Steps)  |
| Tabu Search                         |  3393 |                129 |                          323 |         9.4731e+06 |    8.71964e+06 |            3.07424 |              221 |      0.338917 | 31min<br/>(for 3393 Steps)  |
| Tabu Search Random                  |    35 |                 11 |                            0 |        9.01121e+06 |    8.77325e+06 |            2.24764 |               14 |       1.19283 | 1min<br/>(for 35 Steps)     |

##### Pareto Front Images

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

---

### Consulta Data Mining

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 77,00 | 32,00 | 24,00 |
| Reference Random  | 50,00 | 25,00 | 21,00 |
| Reference Optimos | 77,00 | 30,00 | 28,00 |
| SA                | 26,00 | 19,00 | 6,00  |
| Tabu Search       | 42,00 | 21,00 | 13,00 |
| PPO               | 50,00 | 28,00 | 30,00 |
| Tabu Random       | 29,00 | 10,00 | 9,00  |
| SA Random         | 34,00 | 21,00 | 10,00 |
| PPO Random        | 34,00 | 15,00 | 16,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,98 | 0,99 | 1,00 |
| Reference Optimos | 1,00 | 0,96 | 0,99 |
| SA                | 0,73 | 0,70 | 0,97 |
| Tabu Search       | 0,87 | 0,96 | 0,98 |
| PPO               | 0,99 | 0,82 | 0,99 |
| Tabu Random       | 0,88 | 0,63 | 0,97 |
| SA Random         | 0,81 | 0,98 | 1,00 |
| PPO Random        | 0,97 | 0,61 | 0,98 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid       | Hard      |
| ----------------- | --------- | --------- | --------- |
| Reference Random  | 2.833,58  | 1.319,03  | 18.702,87 |
| Reference Optimos | 3,08      | 90.263,12 | 35.620,70 |
| SA                | 7.078,89  | 90.612,63 | 78.466,39 |
| Tabu Search       | 11.310,39 | 90.300,65 | 62.127,93 |
| PPO               | 981,75    | 92.517,95 | 36.111,28 |
| Tabu Random       | 4.486,89  | 91.019,64 | 56.746,92 |
| SA Random         | 38.498,23 | 1.372,92  | 19.515,43 |
| PPO Random        | 3.219,77  | 93.659,12 | 69.173,02 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,12 | 1,72 | 1,60 |
| Reference Optimos | 1,20 | 1,01 | 1,09 |
| SA                | 1,05 | 1,02 | 1,01 |
| Tabu Search       | 0,95 | 1,01 | 1,03 |
| PPO               | 1,11 | 1,01 | 1,06 |
| Tabu Random       | 0,98 | 1,02 | 1,00 |
| SA Random         | 1,38 | 1,63 | 1,49 |
| PPO Random        | 1,01 | 1,00 | 0,99 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,01 | 0,16 | 0,25 |
| Reference Optimos | 0,99 | 0,84 | 0,75 |
| SA                | 0,06 | 0,19 | 0,00 |
| Tabu Search       | 0,58 | 0,66 | 0,42 |
| PPO               | 0,36 | 0,00 | 0,33 |
| Tabu Random       | 0,01 | 0,03 | 0,00 |
| SA Random         | 0,01 | 0,12 | 0,21 |
| PPO Random        | 0,00 | 0,00 | 0,04 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 10.924.190,73 | 11.498.316,15 | 11.845.078,32 |
| Reference         | 11.505.477,29 | 11.360.135,58 | 12.438.262,75 |
| Reference Random  | 11.595.106,20 | 11.443.018,69 | 11.625.892,84 |
| Reference Optimos | 11.510.016,25 | 11.401.558,01 | 12.432.425,07 |
| SA                | 11.523.864,35 | 11.760.911,87 | 11.371.253,37 |
| Tabu Search       | 11.397.259,22 | 11.343.615,08 | 14.404.102,38 |
| PPO               | 11.573.728,00 | 11.892.906,21 | 12.519.200,95 |
| Tabu Random       | 11.899.980,67 | 11.533.807,71 | 11.899.414,42 |
| SA Random         | 11.487.427,01 | 11.406.146,05 | 11.686.354,37 |
| PPO Random        | 11.582.461,74 | 11.581.298,14 | 11.884.449,70 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 10.924.190,73 | 11.498.316,15 | 11.845.078,32 |
| Reference         | 10.653.552,98 | 10.906.582,86 | 10.908.571,55 |
| Reference Random  | 10.908.046,39 | 10.867.316,03 | 10.912.591,09 |
| Reference Optimos | 10.653.552,98 | 10.906.582,86 | 10.908.571,55 |
| SA                | 10.899.817,14 | 11.162.809,30 | 11.150.692,54 |
| Tabu Search       | 10.653.552,98 | 10.906.582,86 | 10.908.571,55 |
| PPO               | 10.559.397,46 | 11.248.319,30 | 11.182.600,34 |
| Tabu Random       | 10.924.190,73 | 10.917.768,17 | 11.250.920,54 |
| SA Random         | 10.908.046,39 | 10.917.768,17 | 11.246.504,00 |
| PPO Random        | 10.729.651,35 | 10.867.316,03 | 11.250.920,54 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Consulta_Data_Mining_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  6611 |               1806 |                              |        1.15599e+07 |    1.05594e+07 |            2.38727 |             6620 |       5.96561 | 717min<br/>(for 6611 Steps)  |
| Proximal Policy Optimization Random |  6951 |               1536 |                              |        1.16295e+07 |    1.07297e+07 |            2.25017 |             6960 |       6.38168 | 718min<br/>(for 6951 Steps)  |
| Simulated Annealing                 | 10012 |                897 |                         2623 |        1.15301e+07 |    1.08998e+07 |            2.65326 |              505 |       1.82837 | 112min<br/>(for 10012 Steps) |
| Simulated Annealing Random          |  1976 |                953 |                            0 |        1.15087e+07 |     1.0908e+07 |            2.86636 |              656 |       2.43394 | 92min<br/>(for 1976 Steps)   |
| Tabu Search                         | 10009 |               3770 |                         1811 |        1.14301e+07 |    1.06536e+07 |             3.1152 |              497 |        1.9764 | 135min<br/>(for 10009 Steps) |
| Tabu Search Random                  |   611 |                292 |                            0 |        1.19551e+07 |    1.10942e+07 |            2.72866 |              200 |       2.85947 | 30min<br/>(for 611 Steps)    |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Consulta_Data_Mining_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  8191 |               1536 |                              |        1.25242e+07 |    1.12337e+07 |            4.74331 |             8200 |        5.6872 | 718min<br/>(for 8191 Steps)  |
| Proximal Policy Optimization Random |  9831 |                595 |                              |        1.18351e+07 |    1.08675e+07 |            3.41973 |             9840 |       3.92619 | 717min<br/>(for 9831 Steps)  |
| Simulated Annealing                 | 10011 |               1039 |                           61 |        1.13937e+07 |    1.11507e+07 |            3.20584 |              536 |     0.0011173 | 142min<br/>(for 10011 Steps) |
| Simulated Annealing Random          |  1084 |                480 |                            0 |        1.18439e+07 |    1.13304e+07 |            4.63462 |              357 |       2.51622 | 47min<br/>(for 1084 Steps)   |
| Tabu Search                         |  3893 |                156 |                          407 |        1.53945e+07 |    1.09086e+07 |            4.27273 |              210 |      0.696202 | 47min<br/>(for 3893 Steps)   |
| Tabu Search Random                  |    83 |                 26 |                            0 |        1.19013e+07 |    1.12509e+07 |            2.58917 |               25 |     0.0934325 | 3min<br/>(for 83 Steps)      |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Consulta_Data_Mining_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  8401 |               2371 |                              |        1.18794e+07 |    1.12483e+07 |            4.20479 |             8410 |       4.76213 | 717min<br/>(for 8401 Steps) |
| Proximal Policy Optimization Random |  8621 |               2491 |                              |        1.15323e+07 |    1.08673e+07 |             2.2739 |             8630 |        5.6891 | 717min<br/>(for 8621 Steps) |
| Simulated Annealing                 |  9993 |               1028 |                         1435 |        1.17937e+07 |    1.13394e+07 |            3.71206 |              538 |       1.57184 | 121min<br/>(for 9993 Steps) |
| Simulated Annealing Random          |  1433 |                755 |                            0 |        1.14658e+07 |    1.10758e+07 |            3.30315 |              475 |      0.267463 | 63min<br/>(for 1433 Steps)  |
| Tabu Search                         |  9994 |               1443 |                         1374 |        1.14417e+07 |    1.09137e+07 |            2.24465 |              508 |       3.14961 | 115min<br/>(for 9994 Steps) |
| Tabu Search Random                  |    95 |                 29 |                            0 |        1.16251e+07 |    1.12549e+07 |            3.58079 |               29 |       1.82635 | 3min<br/>(for 95 Steps)     |

##### Pareto Front Images

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

---

### Gov

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 17,00 | 26,00 | 7,00  |
| Reference Random  | 9,00  | 17,00 | 5,00  |
| Reference Optimos | 25,00 | 24,00 | 10,00 |
| SA                | 13,00 | 14,00 | 8,00  |
| Tabu Search       | 16,00 | 23,00 | 9,00  |
| PPO               | 18,00 | 9,00  | 3,00  |
| Tabu Random       | 4,00  | 9,00  | 6,00  |
| SA Random         | 6,00  | 13,00 | 5,00  |
| PPO Random        | 8,00  | 10,00 | 3,00  |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,95 | 0,98 | 0,99 |
| Reference Optimos | 1,00 | 1,00 | 1,00 |
| SA                | 0,92 | 0,98 | 1,00 |
| Tabu Search       | 0,94 | 1,00 | 1,00 |
| PPO               | 1,00 | 0,99 | 0,96 |
| Tabu Random       | 0,82 | 0,95 | 0,97 |
| SA Random         | 0,82 | 0,93 | 0,99 |
| PPO Random        | 0,95 | 0,98 | 0,97 |

<br>

##### Hausdorff

| Agent / Reference | Easy       | Mid        | Hard      |
| ----------------- | ---------- | ---------- | --------- |
| Reference Random  | 51.182,11  | 390.275,62 | 4.786,74  |
| Reference Optimos | 8.498,87   | 601,78     | 3.742,73  |
| SA                | 139.807,66 | 399.659,68 | 12.229,69 |
| Tabu Search       | 42.046,65  | 1.052,23   | 3.611,52  |
| PPO               | 16.998,45  | 194.094,43 | 18.849,23 |
| Tabu Random       | 189.850,69 | 455.733,28 | 10.109,15 |
| SA Random         | 175.418,86 | 478.082,00 | 4.786,74  |
| PPO Random        | 52.002,22  | 402.914,79 | 16.354,39 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,98 | 1,19 | 1,11 |
| Reference Optimos | 1,17 | 1,03 | 0,92 |
| SA                | 1,28 | 1,17 | 1,12 |
| Tabu Search       | 0,94 | 1,02 | 0,84 |
| PPO               | 0,87 | 1,06 | 0,94 |
| Tabu Random       | 1,24 | 1,11 | 0,32 |
| SA Random         | 1,29 | 1,27 | 1,11 |
| PPO Random        | 0,95 | 1,05 | 0,88 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,35 | 0,15 | 0,71 |
| Reference Optimos | 0,65 | 0,85 | 0,29 |
| SA                | 0,35 | 0,00 | 0,14 |
| Tabu Search       | 0,00 | 0,85 | 0,14 |
| PPO               | 0,29 | 0,00 | 0,00 |
| Tabu Random       | 0,00 | 0,00 | 0,00 |
| SA Random         | 0,06 | 0,08 | 0,71 |
| PPO Random        | 0,29 | 0,08 | 0,00 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 13.369.643,07 | 16.047.474,92 | 15.756.570,78 |
| Reference         | 20.382.094,57 | 13.905.885,40 | 17.864.736,16 |
| Reference Random  | 18.702.461,88 | 32.724.482,55 | 16.897.205,28 |
| Reference Optimos | 20.768.290,18 | 13.521.404,64 | 19.964.244,16 |
| SA                | 19.893.274,06 | 28.990.146,10 | 19.213.421,38 |
| Tabu Search       | 20.151.717,82 | 13.179.858,35 | 18.573.617,82 |
| PPO               | 22.807.284,80 | 53.598.662,45 | 16.241.664,63 |
| Tabu Random       | 17.216.198,55 | 29.225.441,19 | 18.454.174,16 |
| SA Random         | 17.674.868,00 | 22.470.807,00 | 16.897.205,28 |
| PPO Random        | 19.708.624,27 | 53.107.122,04 | 19.719.892,00 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 13.369.643,07 | 16.047.474,92 | 15.756.570,78 |
| Reference         | 15.788.366,74 | 10.521.791,54 | 14.582.036,26 |
| Reference Random  | 14.811.805,42 | 14.796.008,26 | 14.582.036,26 |
| Reference Optimos | 15.788.366,74 | 10.521.791,54 | 14.914.682,03 |
| SA                | 15.788.366,74 | 13.734.908,48 | 13.402.862,80 |
| Tabu Search       | 16.655.749,35 | 10.521.791,54 | 14.914.682,03 |
| PPO               | 13.369.643,07 | 16.357.230,91 | 15.756.570,78 |
| Tabu Random       | 14.480.629,67 | 16.723.485,01 | 17.763.490,08 |
| SA Random         | 14.811.805,42 | 15.523.152,37 | 14.582.036,26 |
| PPO Random        | 16.639.415,98 | 14.796.008,26 | 15.756.570,78 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Gov_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Gov_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Gov_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time       |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :---------------------------- |
| Proximal Policy Optimization        |  2951 |               1513 |                              |        2.29747e+07 |    1.65511e+07 |            3.71509 |             2960 |       27.4838 | 1,431min<br/>(for 2951 Steps) |
| Proximal Policy Optimization Random |    40 |               1292 |                              |        1.97086e+07 |    1.66394e+07 |            3.69476 |             2141 |       6664.29 | 1,016min<br/>(for 40 Steps)   |
| Simulated Annealing                 |  9996 |                380 |                         5397 |        1.98933e+07 |    1.57884e+07 |            2.13291 |              436 |       1.81164 | 513min<br/>(for 9996 Steps)   |
| Simulated Annealing Random          |   680 |                283 |                            0 |        1.77299e+07 |    1.48118e+07 |            2.02718 |              224 |       16.4456 | 178min<br/>(for 680 Steps)    |
| Tabu Search                         |  2105 |                279 |                            0 |        1.96246e+07 |    1.66557e+07 |            2.11111 |              107 |       1.12742 | 89min<br/>(for 2105 Steps)    |
| Tabu Search Random                  |    35 |                  9 |                            0 |        1.63184e+07 |    1.44806e+07 |            2.11628 |                9 |       13.3734 | 4min<br/>(for 35 Steps)       |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Gov_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Gov_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Gov_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |   995 |               1002 |                              |        1.70208e+07 |    1.58872e+07 |                2.4 |             1005 |       8.21465 | 73min<br/>(for 995 Steps)   |
| Proximal Policy Optimization Random |  1114 |                955 |                              |        2.02035e+07 |    1.72073e+07 |            2.05263 |             1124 |       8.24061 | 141min<br/>(for 1114 Steps) |
| Simulated Annealing                 |    81 |                  2 |                           57 |         2.2491e+07 |    1.57653e+07 |            2.10574 |                4 |      0.001033 | 5min<br/>(for 81 Steps)     |
| Simulated Annealing Random          |   648 |                260 |                            0 |        1.68972e+07 |     1.4582e+07 |            2.10256 |              208 |        12.569 | 198min<br/>(for 648 Steps)  |
| Tabu Search                         |   978 |                 21 |                            0 |         1.8935e+07 |    1.49147e+07 |            2.12903 |               47 |      0.361706 | 167min<br/>(for 978 Steps)  |
| Tabu Search Random                  |    44 |                 10 |                            0 |        1.86589e+07 |    1.57566e+07 |            2.09605 |               12 |       12.8511 | 12min<br/>(for 44 Steps)    |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Gov_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Gov_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Gov_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Gov_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Gov_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Gov_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Gov_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Gov_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time       |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :---------------------------- |
| Proximal Policy Optimization        |  1731 |                311 |                              |        5.06741e+07 |    1.63572e+07 |            4.92711 |             1740 |       57.1054 | 1,424min<br/>(for 1731 Steps) |
| Proximal Policy Optimization Random |    31 |                  2 |                              |        2.06983e+07 |    1.87449e+07 |            2.46479 |               40 |       28.9958 | 14min<br/>(for 31 Steps)      |
| Simulated Annealing                 |  9996 |                261 |                         5965 |        2.84575e+07 |    1.37349e+07 |            4.65205 |              436 |       1.25878 | 736min<br/>(for 9996 Steps)   |
| Simulated Annealing Random          |   760 |                329 |                            0 |        2.25602e+07 |    1.55232e+07 |            2.03125 |              245 |       13.5362 | 220min<br/>(for 760 Steps)    |
| Tabu Search                         |  5119 |                251 |                            0 |        1.33973e+07 |    1.05218e+07 |            2.53326 |              263 |       5.93512 | 297min<br/>(for 5119 Steps)   |
| Tabu Search Random                  |   125 |                 35 |                            0 |        3.18784e+07 |    1.67235e+07 |             2.0061 |               39 |       10.9127 | 35min<br/>(for 125 Steps)     |

##### Pareto Front Images

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

---

### Insurance

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy   | Mid   | Hard  |
| ----------------- | ------ | ----- | ----- |
| Reference         | 102,00 | 35,00 | 9,00  |
| Reference Random  | 49,00  | 18,00 | 11,00 |
| Reference Optimos | 83,00  | 35,00 | 9,00  |
| SA                | 35,00  | 15,00 | 9,00  |
| Tabu Search       | 66,00  | 24,00 | 9,00  |
| PPO               | 34,00  | 19,00 | 6,00  |
| Tabu Random       | 20,00  | 10,00 | 2,00  |
| SA Random         | 42,00  | 15,00 | 4,00  |
| PPO Random        | 23,00  | 15,00 | 13,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 0,96 | 1,00 |
| Reference Optimos | 0,86 | 1,00 | 1,00 |
| SA                | 0,63 | 0,67 | 1,00 |
| Tabu Search       | 0,86 | 0,65 | 1,00 |
| PPO               | 0,84 | 0,99 | 1,00 |
| Tabu Random       | 0,76 | 0,72 | 1,00 |
| SA Random         | 1,00 | 0,96 | 1,00 |
| PPO Random        | 0,73 | 0,83 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid      | Hard     |
| ----------------- | --------- | -------- | -------- |
| Reference Random  | 820,72    | 2.021,48 | 405,81   |
| Reference Optimos | 20.828,96 | 300,91   | 0,00     |
| SA                | 25.189,49 | 8.911,26 | 239,13   |
| Tabu Search       | 20.873,41 | 9.904,22 | 514,92   |
| PPO               | 22.266,42 | 1.265,45 | 6.938,30 |
| Tabu Random       | 23.137,72 | 5.116,44 | 694,27   |
| SA Random         | 1.089,10  | 2.175,18 | 731,99   |
| PPO Random        | 22.317,59 | 2.574,28 | 360,41   |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,20 | 1,12 | 0,90 |
| Reference Optimos | 0,97 | 0,97 | 1,08 |
| SA                | 0,98 | 1,00 | 1,21 |
| Tabu Search       | 0,97 | 1,01 | 0,86 |
| PPO               | 0,99 | 0,79 | 1,24 |
| Tabu Random       | 0,96 | 0,96 | 0,69 |
| SA Random         | 1,13 | 1,23 | 0,73 |
| PPO Random        | 0,98 | 0,71 | 0,81 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,19 | 0,11 | 0,00 |
| Reference Optimos | 0,81 | 0,89 | 1,00 |
| SA                | 0,17 | 0,26 | 0,22 |
| Tabu Search       | 0,64 | 0,34 | 0,67 |
| PPO               | 0,01 | 0,34 | 0,22 |
| Tabu Random       | 0,01 | 0,03 | 0,11 |
| SA Random         | 0,17 | 0,11 | 0,11 |
| PPO Random        | 0,01 | 0,03 | 0,11 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 21.523.074,51 | 21.367.016,55 | 21.992.001,65 |
| Reference         | 22.163.701,21 | 22.480.273,77 | 21.980.061,32 |
| Reference Random  | 22.520.861,70 | 22.715.030,13 | 22.230.347,40 |
| Reference Optimos | 21.940.447,08 | 22.319.156,40 | 21.980.061,32 |
| SA                | 21.997.410,60 | 21.882.992,74 | 21.868.122,18 |
| Tabu Search       | 21.931.262,97 | 22.084.117,64 | 22.034.900,76 |
| PPO               | 21.866.011,73 | 22.512.018,90 | 22.017.415,53 |
| Tabu Random       | 21.910.472,47 | 22.448.677,25 | 21.575.390,94 |
| SA Random         | 22.575.855,21 | 22.727.193,86 | 21.591.259,18 |
| PPO Random        | 21.976.390,66 | 22.504.743,76 | 22.192.879,69 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 21.523.074,51 | 21.367.016,55 | 21.992.001,65 |
| Reference         | 21.072.069,32 | 21.367.016,55 | 21.506.333,06 |
| Reference Random  | 21.265.421,23 | 21.209.398,29 | 21.840.288,41 |
| Reference Optimos | 21.072.069,32 | 21.449.581,76 | 21.506.333,06 |
| SA                | 20.944.858,00 | 21.367.016,55 | 21.221.099,75 |
| Tabu Search       | 21.072.069,32 | 21.288.200,25 | 21.776.404,35 |
| PPO               | 20.709.108,80 | 21.250.656,59 | 21.517.242,02 |
| Tabu Random       | 21.285.666,80 | 21.367.016,55 | 21.370.047,01 |
| SA Random         | 21.265.421,23 | 21.282.481,73 | 21.370.047,01 |
| PPO Random        | 21.114.791,87 | 21.209.398,29 | 21.780.734,88 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Insurance_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Insurance_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Insurance_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  7031 |               2074 |                              |        2.18687e+07 |    2.07091e+07 |             2.2981 |             7040 |       5.88667 | 718min<br/>(for 7031 Steps) |
| Proximal Policy Optimization Random |  6371 |                576 |                              |        2.18484e+07 |    2.11148e+07 |             2.0819 |             6380 |       7.42354 | 718min<br/>(for 6371 Steps) |
| Simulated Annealing                 |  9996 |                331 |                          531 |        2.20013e+07 |    2.09449e+07 |                  2 |              675 |       1.37837 | 147min<br/>(for 9996 Steps) |
| Simulated Annealing Random          |  1592 |                609 |                            0 |        2.26663e+07 |    2.12654e+07 |            5.37885 |              532 |       2.87519 | 99min<br/>(for 1592 Steps)  |
| Tabu Search                         |  9992 |                261 |                          539 |        2.19604e+07 |    2.10721e+07 |                  2 |              582 |       25.6315 | 159min<br/>(for 9992 Steps) |
| Tabu Search Random                  |   266 |                 96 |                            0 |        2.20979e+07 |    2.15495e+07 |                  2 |               90 |       2.74988 | 16min<br/>(for 266 Steps)   |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Insurance_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Insurance_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Insurance_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  3259 |                388 |                              |        2.23003e+07 |    2.15172e+07 |                  2 |             3269 |       6.66236 | 287min<br/>(for 3259 Steps)  |
| Proximal Policy Optimization Random |  7361 |                650 |                              |        2.22657e+07 |    2.18403e+07 |                  2 |             7370 |       6.16649 | 718min<br/>(for 7361 Steps)  |
| Simulated Annealing                 | 10008 |                385 |                           33 |         2.1984e+07 |    2.12211e+07 |                  2 |              693 |     0.0935161 | 162min<br/>(for 10008 Steps) |
| Simulated Annealing Random          |   704 |                355 |                            0 |        2.21125e+07 |     2.1791e+07 |            2.99432 |              236 |       3.75098 | 44min<br/>(for 704 Steps)    |
| Tabu Search                         |  3862 |                117 |                         1117 |        2.21161e+07 |    2.17764e+07 |                  2 |              257 |       0.96359 | 60min<br/>(for 3862 Steps)   |
| Tabu Search Random                  |     8 |                  2 |                            0 |         2.2355e+07 |    2.20561e+07 |                  0 |                4 |       3.28029 | 0min<br/>(for 8 Steps)       |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Insurance_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Insurance_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Insurance_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Insurance_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Insurance_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Insurance_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Insurance_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Insurance_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  5891 |                213 |                              |        2.25286e+07 |    2.12507e+07 |            2.27108 |             5900 |       5.97208 | 718min<br/>(for 5891 Steps)  |
| Proximal Policy Optimization Random |  2741 |                 81 |                              |        2.24371e+07 |    2.12094e+07 |            2.11444 |             2750 |       18.2748 | 716min<br/>(for 2741 Steps)  |
| Simulated Annealing                 | 10006 |                372 |                          135 |        2.19224e+07 |    2.14326e+07 |                  2 |              691 |      0.402094 | 145min<br/>(for 10006 Steps) |
| Simulated Annealing Random          |   821 |                389 |                            0 |        2.30258e+07 |    2.19076e+07 |            2.95062 |              274 |       3.65792 | 51min<br/>(for 821 Steps)    |
| Tabu Search                         |  7908 |                250 |                          973 |        2.21005e+07 |    2.12882e+07 |                  2 |              521 |       2.20827 | 125min<br/>(for 7908 Steps)  |
| Tabu Search Random                  |   173 |                 56 |                            0 |         2.2328e+07 |    2.15111e+07 |                  2 |               59 |      0.200568 | 10min<br/>(for 173 Steps)    |

##### Pareto Front Images

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

---

### Production

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 80,00 | 44,00 | 13,00 |
| Reference Random  | 76,00 | 41,00 | 12,00 |
| Reference Optimos | 69,00 | 44,00 | 16,00 |
| SA                | 37,00 | 30,00 | 12,00 |
| Tabu Search       | 47,00 | 44,00 | 18,00 |
| PPO               | 50,00 | 41,00 | 8,00  |
| Tabu Random       | 41,00 | 15,00 | 8,00  |
| SA Random         | 35,00 | 17,00 | 8,00  |
| PPO Random        | 45,00 | 39,00 | 13,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,96 | 0,86 | 1,00 |
| Reference Optimos | 0,99 | 1,00 | 1,00 |
| SA                | 0,68 | 0,80 | 0,98 |
| Tabu Search       | 0,94 | 0,88 | 1,00 |
| PPO               | 0,94 | 0,94 | 0,98 |
| Tabu Random       | 0,78 | 0,60 | 0,98 |
| SA Random         | 0,73 | 0,68 | 1,00 |
| PPO Random        | 0,90 | 0,84 | 0,98 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid        | Hard      |
| ----------------- | --------- | ---------- | --------- |
| Reference Random  | 11.943,84 | 57.288,56  | 13.093,12 |
| Reference Optimos | 1.231,15  | 0,00       | 16.105,32 |
| SA                | 44.380,42 | 145.330,56 | 32.912,96 |
| Tabu Search       | 32.572,43 | 96.853,24  | 16.542,56 |
| PPO               | 3.905,48  | 11.508,62  | 54.021,29 |
| Tabu Random       | 44.322,42 | 140.492,35 | 35.702,53 |
| SA Random         | 9.194,47  | 141.978,28 | 13.963,67 |
| PPO Random        | 19.913,55 | 58.921,94  | 25.432,49 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,97 | 0,96 | 1,33 |
| Reference Optimos | 0,95 | 1,09 | 0,99 |
| SA                | 0,97 | 0,97 | 1,17 |
| Tabu Search       | 0,88 | 1,00 | 1,06 |
| PPO               | 0,97 | 0,98 | 0,99 |
| Tabu Random       | 0,97 | 1,00 | 1,01 |
| SA Random         | 1,25 | 0,97 | 1,15 |
| PPO Random        | 0,83 | 0,97 | 1,37 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,53 | 0,00 | 0,31 |
| Reference Optimos | 0,47 | 1,00 | 0,69 |
| SA                | 0,04 | 0,09 | 0,00 |
| Tabu Search       | 0,26 | 0,61 | 0,54 |
| PPO               | 0,17 | 0,30 | 0,15 |
| Tabu Random       | 0,45 | 0,00 | 0,00 |
| SA Random         | 0,07 | 0,00 | 0,23 |
| PPO Random        | 0,00 | 0,00 | 0,08 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 42.044.521,00 | 41.035.979,10 | 41.461.760,95 |
| Reference         | 42.190.396,40 | 42.625.614,35 | 42.689.935,34 |
| Reference Random  | 42.366.701,18 | 42.561.152,22 | 42.480.832,52 |
| Reference Optimos | 42.179.962,73 | 42.625.614,35 | 42.651.001,36 |
| SA                | 42.295.871,86 | 42.079.724,37 | 42.323.845,15 |
| Tabu Search       | 42.150.131,94 | 42.650.766,40 | 42.692.566,31 |
| PPO               | 42.229.110,27 | 42.672.010,76 | 42.214.365,71 |
| Tabu Random       | 42.198.516,53 | 41.983.662,10 | 41.447.310,40 |
| SA Random         | 42.334.991,62 | 42.370.681,44 | 42.297.213,99 |
| PPO Random        | 42.507.066,35 | 42.483.845,26 | 42.512.857,09 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 42.044.521,00 | 41.035.979,10 | 41.461.760,95 |
| Reference         | 40.511.363,26 | 40.891.617,05 | 41.496.367,12 |
| Reference Random  | 40.511.363,26 | 40.924.274,21 | 41.510.903,62 |
| Reference Optimos | 40.615.200,00 | 40.891.617,05 | 41.496.367,12 |
| SA                | 41.215.377,05 | 40.649.684,84 | 40.341.465,75 |
| Tabu Search       | 40.889.476,81 | 40.891.617,05 | 41.222.681,50 |
| PPO               | 40.297.020,43 | 40.937.649,95 | 41.448.152,63 |
| Tabu Random       | 40.511.363,26 | 40.649.684,84 | 40.341.465,75 |
| SA Random         | 41.149.958,32 | 40.957.056,09 | 40.341.465,75 |
| PPO Random        | 41.098.342,91 | 40.403.956,28 | 41.510.903,62 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Production_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Production_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Production_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  5181 |                433 |                              |        4.22143e+07 |     4.0297e+07 |            2.51078 |             5190 |       8.38344 | 718min<br/>(for 5181 Steps) |
| Proximal Policy Optimization Random |  5407 |                715 |                              |        4.25095e+07 |    4.10983e+07 |            2.15238 |             5417 |       6.30004 | 538min<br/>(for 5407 Steps) |
| Simulated Annealing                 | 10001 |                909 |                         4850 |        4.24021e+07 |    4.12154e+07 |                  2 |              510 |       0.18976 | 85min<br/>(for 10001 Steps) |
| Simulated Annealing Random          |  2626 |               1076 |                           22 |        4.23852e+07 |      4.115e+07 |            3.20748 |              868 |       1.39887 | 94min<br/>(for 2626 Steps)  |
| Tabu Search                         |  9991 |               1613 |                         1150 |        4.21807e+07 |    4.08895e+07 |            2.91931 |              470 |     0.0067332 | 92min<br/>(for 9991 Steps)  |
| Tabu Search Random                  |  2378 |                967 |                            0 |        4.22467e+07 |    4.05114e+07 |            2.42581 |              790 |       1.83766 | 82min<br/>(for 2378 Steps)  |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Production_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Production_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Production_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  5999 |                198 |                              |        4.26699e+07 |    4.14482e+07 |            2.69663 |             6009 |        4.8629 | 501min<br/>(for 5999 Steps) |
| Proximal Policy Optimization Random |  9991 |                454 |                              |        4.27135e+07 |    4.15109e+07 |            2.83544 |            10000 |       4.04198 | 683min<br/>(for 9991 Steps) |
| Simulated Annealing                 | 10006 |               1142 |                          478 |          4.275e+07 |    4.14388e+07 |            13.5676 |              478 |      0.131001 | 77min<br/>(for 10006 Steps) |
| Simulated Annealing Random          |   839 |                363 |                            0 |        4.25681e+07 |    4.18752e+07 |            16.7407 |              274 |       1.79834 | 30min<br/>(for 839 Steps)   |
| Tabu Search                         |  6988 |                421 |                         1607 |        4.27518e+07 |    4.12227e+07 |                2.6 |              349 |      0.196693 | 51min<br/>(for 6988 Steps)  |
| Tabu Search Random                  |   128 |                 38 |                            0 |        4.20802e+07 |    4.10975e+07 |            2.61017 |               40 |       1.43653 | 3min<br/>(for 128 Steps)    |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Production_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Production_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Production_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Production_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Production_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Production_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Production_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Production_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  8051 |               2676 |                              |        4.27068e+07 |    4.09376e+07 |            3.06264 |             8060 |       5.65617 | 718min<br/>(for 8051 Steps) |
| Proximal Policy Optimization Random |  8751 |               1528 |                              |        4.25273e+07 |     4.0404e+07 |             2.1759 |             8760 |       4.94335 | 718min<br/>(for 8751 Steps) |
| Simulated Annealing                 | 10008 |               1185 |                         4965 |        4.21387e+07 |    4.06497e+07 |            3.35955 |              533 |      0.151647 | 84min<br/>(for 10008 Steps) |
| Simulated Annealing Random          |  1067 |                494 |                            0 |        4.25709e+07 |     4.1036e+07 |            2.73571 |              353 |       2.06465 | 35min<br/>(for 1067 Steps)  |
| Tabu Search                         |  9996 |               2104 |                         1121 |        4.27049e+07 |    4.08916e+07 |            2.44721 |              528 |       1.03266 | 83min<br/>(for 9996 Steps)  |
| Tabu Search Random                  |   272 |                107 |                            0 |        4.21376e+07 |    4.09571e+07 |            2.53165 |               88 |      0.154355 | 8min<br/>(for 272 Steps)    |

##### Pareto Front Images

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

---

### Purchasing Example

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 84,00 | 67,00 | 21,00 |
| Reference Random  | 63,00 | 36,00 | 11,00 |
| Reference Optimos | 84,00 | 61,00 | 30,00 |
| SA                | 21,00 | 34,00 | 17,00 |
| Tabu Search       | 62,00 | 60,00 | 23,00 |
| PPO               | 41,00 | 31,00 | 9,00  |
| Tabu Random       | 21,00 | 15,00 | 7,00  |
| SA Random         | 19,00 | 21,00 | 5,00  |
| PPO Random        | 55,00 | 33,00 | 11,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,95 | 0,98 | 1,00 |
| Reference Optimos | 1,00 | 0,98 | 1,00 |
| SA                | 0,82 | 0,98 | 1,00 |
| Tabu Search       | 0,88 | 0,94 | 1,00 |
| PPO               | 0,97 | 0,80 | 0,99 |
| Tabu Random       | 0,81 | 0,80 | 1,00 |
| SA Random         | 0,85 | 0,91 | 1,00 |
| PPO Random        | 0,93 | 0,97 | 0,99 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid       | Hard      |
| ----------------- | --------- | --------- | --------- |
| Reference Random  | 8.623,00  | 8.140,31  | 38.482,71 |
| Reference Optimos | 1.182,97  | 8.972,15  | 1.701,43  |
| SA                | 11.506,75 | 9.414,85  | 5.687,71  |
| Tabu Search       | 16.494,34 | 10.951,91 | 2.928,72  |
| PPO               | 3.640,81  | 9.523,58  | 32.184,80 |
| Tabu Random       | 7.035,61  | 9.284,33  | 5.852,66  |
| SA Random         | 6.729,42  | 10.447,49 | 70.349,14 |
| PPO Random        | 8.762,85  | 9.982,97  | 22.409,18 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,93 | 1,18 | 1,14 |
| Reference Optimos | 1,40 | 1,00 | 0,82 |
| SA                | 1,07 | 1,00 | 1,29 |
| Tabu Search       | 0,99 | 0,97 | 0,85 |
| PPO               | 1,06 | 0,97 | 0,98 |
| Tabu Random       | 1,16 | 1,05 | 0,73 |
| SA Random         | 1,08 | 1,11 | 0,98 |
| PPO Random        | 0,94 | 1,05 | 1,06 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,32 | 0,12 | 0,38 |
| Reference Optimos | 0,68 | 0,88 | 0,62 |
| SA                | 0,08 | 0,09 | 0,14 |
| Tabu Search       | 0,42 | 0,81 | 0,48 |
| PPO               | 0,19 | 0,01 | 0,00 |
| Tabu Random       | 0,05 | 0,01 | 0,24 |
| SA Random         | 0,04 | 0,10 | 0,10 |
| PPO Random        | 0,26 | 0,04 | 0,05 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 34.307.437,68 | 34.273.851,12 | 33.988.137,01 |
| Reference         | 35.625.578,32 | 35.418.563,14 | 36.667.798,11 |
| Reference Random  | 35.365.017,14 | 35.964.278,76 | 36.736.667,40 |
| Reference Optimos | 35.408.186,90 | 35.325.624,35 | 36.352.271,30 |
| SA                | 35.380.553,77 | 35.672.985,33 | 35.860.683,28 |
| Tabu Search       | 34.868.499,42 | 35.263.349,91 | 36.583.744,60 |
| PPO               | 36.007.578,64 | 35.828.438,13 | 35.644.030,25 |
| Tabu Random       | 35.209.070,54 | 35.211.262,66 | 36.323.646,62 |
| SA Random         | 35.666.977,63 | 35.342.877,92 | 37.434.647,90 |
| PPO Random        | 35.369.977,71 | 36.650.868,87 | 35.462.892,97 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 34.307.437,68 | 34.273.851,12 | 33.988.137,01 |
| Reference         | 33.668.470,79 | 33.819.249,21 | 34.723.728,97 |
| Reference Random  | 34.226.981,05 | 34.291.066,42 | 34.723.728,97 |
| Reference Optimos | 33.242.624,60 | 33.819.249,21 | 34.261.631,04 |
| SA                | 33.668.470,79 | 33.791.557,40 | 33.988.137,01 |
| Tabu Search       | 33.242.624,60 | 33.819.249,21 | 35.142.270,91 |
| PPO               | 34.288.824,13 | 34.273.851,12 | 34.887.923,36 |
| Tabu Random       | 33.668.470,79 | 34.076.614,29 | 33.988.137,01 |
| SA Random         | 33.668.470,79 | 34.273.851,12 | 34.872.935,94 |
| PPO Random        | 33.760.787,04 | 34.273.851,12 | 33.988.137,01 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Purchasing_Example_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Purchasing_Example_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Purchasing_Example_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time      |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :--------------------------- |
| Proximal Policy Optimization        |  2421 |                  8 |                              |        3.58564e+07 |    3.34401e+07 |            2.11585 |             2430 |        19.487 | 714min<br/>(for 2421 Steps)  |
| Proximal Policy Optimization Random |  2321 |                  6 |                              |        3.54005e+07 |    3.37608e+07 |            2.35095 |             2330 |       18.1589 | 716min<br/>(for 2321 Steps)  |
| Simulated Annealing                 | 10008 |                231 |                          791 |        3.54894e+07 |     3.4329e+07 |            2.01172 |              493 |      0.226194 | 297min<br/>(for 10008 Steps) |
| Simulated Annealing Random          |  1421 |                555 |                          106 |        3.55237e+07 |    3.36685e+07 |            3.26184 |              468 |       9.54707 | 291min<br/>(for 1421 Steps)  |
| Tabu Search                         |  9201 |                100 |                         6024 |        3.49465e+07 |    3.32426e+07 |            2.00156 |              460 |     0.0010273 | 297min<br/>(for 9201 Steps)  |
| Tabu Search Random                  |  2111 |                868 |                          395 |        3.54891e+07 |     3.4227e+07 |            2.11141 |              700 |       7.96246 | 298min<br/>(for 2111 Steps)  |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Purchasing_Example_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Purchasing_Example_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Purchasing_Example_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  2657 |                 19 |                              |         3.5661e+07 |    3.48879e+07 |            2.14517 |             2667 |        11.759 | 620min<br/>(for 2657 Steps) |
| Proximal Policy Optimization Random |  3091 |                 18 |                              |        3.55581e+07 |    3.47432e+07 |            2.31857 |             3100 |       10.7695 | 716min<br/>(for 3091 Steps) |
| Simulated Annealing                 |  6901 |                162 |                         1696 |        3.60005e+07 |    3.39881e+07 |            2.10809 |              338 |       3.16321 | 298min<br/>(for 6901 Steps) |
| Simulated Annealing Random          |  1258 |                541 |                            0 |        3.69597e+07 |    3.48729e+07 |            2.23595 |              414 |       6.03285 | 293min<br/>(for 1258 Steps) |
| Tabu Search                         |  1451 |                 19 |                          110 |         3.6573e+07 |    3.49784e+07 |            3.11605 |               73 |   0.000914311 | 297min<br/>(for 1451 Steps) |
| Tabu Search Random                  |   164 |                 50 |                            0 |        3.65412e+07 |    3.47237e+07 |            2.41566 |               52 |       7.24261 | 37min<br/>(for 164 Steps)   |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Purchasing_Example_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Purchasing_Example_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Purchasing_Example_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Purchasing_Example_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Purchasing_Example_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Purchasing_Example_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Purchasing_Example_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  3121 |                 17 |                              |        3.57782e+07 |    3.45443e+07 |            2.02787 |             3130 |       13.5479 | 716min<br/>(for 3121 Steps) |
| Proximal Policy Optimization Random |  3121 |                 65 |                              |        3.66452e+07 |    3.46787e+07 |            2.11246 |             3130 |       10.9197 | 716min<br/>(for 3121 Steps) |
| Simulated Annealing                 |  9998 |                217 |                         5387 |         3.5673e+07 |    3.37916e+07 |            2.00307 |              480 |      0.819206 | 255min<br/>(for 9998 Steps) |
| Simulated Annealing Random          |  2231 |                983 |                           74 |        3.55964e+07 |    3.42911e+07 |             2.3916 |              738 |       10.7407 | 297min<br/>(for 2231 Steps) |
| Tabu Search                         |  9621 |                124 |                         4583 |        3.52817e+07 |    3.39773e+07 |            2.01115 |              498 |      0.001052 | 298min<br/>(for 9621 Steps) |
| Tabu Search Random                  |   197 |                 75 |                            0 |        3.54491e+07 |    3.45946e+07 |             2.0785 |               63 |       8.48498 | 25min<br/>(for 197 Steps)   |

##### Pareto Front Images

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

---

### Sepsis Das

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 27,00 | 8,00  | 7,00  |
| Reference Random  | 19,00 | 5,00  | 7,00  |
| Reference Optimos | 25,00 | 12,00 | 5,00  |
| SA                | 2,00  | 8,00  | 8,00  |
| Tabu Search       | 11,00 | 14,00 | 2,00  |
| PPO               | 25,00 | 10,00 | 3,00  |
| Tabu Random       | 9,00  | 1,00  | 1,00  |
| SA Random         | 15,00 | 5,00  | 12,00 |
| PPO Random        | 7,00  | 10,00 | 5,00  |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 1,00 | 1,00 |
| Reference Optimos | 1,00 | 0,94 | 0,95 |
| SA                | 0,64 | 0,56 | 0,95 |
| Tabu Search       | 1,00 | 0,85 | 0,95 |
| PPO               | 1,00 | 0,93 | 0,95 |
| Tabu Random       | 0,91 | 0,51 | 0,95 |
| SA Random         | 1,00 | 1,00 | 1,00 |
| PPO Random        | 0,75 | 0,59 | 0,95 |

<br>

##### Hausdorff

| Agent / Reference | Easy      | Mid          | Hard       |
| ----------------- | --------- | ------------ | ---------- |
| Reference Random  | 18.889,32 | 11.197,12    | 0,00       |
| Reference Optimos | 13.178,20 | 342.611,80   | 827.929,58 |
| SA                | 46.659,30 | 559.260,76   | 763.095,91 |
| Tabu Search       | 45.575,56 | 206.833,75   | 179.710,58 |
| PPO               | 18.746,65 | 369.574,35   | 311.571,90 |
| Tabu Random       | 60.559,17 | 640.252,01   | 218.352,75 |
| SA Random         | 18.465,39 | 11.197,12    | 0,00       |
| PPO Random        | 58.972,12 | 1.385.123,39 | 287.407,49 |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,03 | 1,18 | 0,44 |
| Reference Optimos | 0,89 | 0,88 | 0,71 |
| SA                | 0,88 | 0,91 | 0,84 |
| Tabu Search       | 1,39 | 0,71 | 0,86 |
| PPO               | 0,84 | 0,95 | 0,81 |
| Tabu Random       | 0,98 | 0,00 | 0,00 |
| SA Random         | 0,84 | 1,18 | 0,44 |
| PPO Random        | 0,95 | 1,11 | 0,84 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,07 | 0,62 | 1,00 |
| Reference Optimos | 0,93 | 0,38 | 0,00 |
| SA                | 0,00 | 0,00 | 0,00 |
| Tabu Search       | 0,33 | 0,38 | 0,00 |
| PPO               | 0,59 | 0,00 | 0,00 |
| Tabu Random       | 0,04 | 0,00 | 0,00 |
| SA Random         | 0,04 | 0,62 | 1,00 |
| PPO Random        | 0,00 | 0,00 | 0,00 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy          | Mid            | Hard           |
| ----------------- | ------------- | -------------- | -------------- |
| Base              | 81.884.663,83 | 78.354.184,84  | 77.382.542,97  |
| Reference         | 48.953.445,18 | 90.904.175,17  | 118.667.196,38 |
| Reference Random  | 49.748.043,43 | 100.127.438,39 | 118.667.196,38 |
| Reference Optimos | 48.887.886,84 | 86.763.900,52  | 79.868.329,19  |
| SA                | 48.981.957,29 | 75.362.790,22  | 79.854.360,14  |
| Tabu Search       | 49.340.890,25 | 78.094.062,27  | 77.669.925,99  |
| PPO               | 48.852.202,85 | 92.318.161,88  | 80.056.716,20  |
| Tabu Random       | 49.408.974,71 | 75.073.704,05  | 77.983.503,98  |
| SA Random         | 49.981.451,71 | 100.127.438,39 | 118.667.196,38 |
| PPO Random        | 48.593.383,09 | 74.766.027,53  | 79.378.748,37  |

<br>

##### Best Cycle Time

| Agent / Reference | Easy          | Mid           | Hard          |
| ----------------- | ------------- | ------------- | ------------- |
| Base              | 81.884.663,83 | 78.354.184,84 | 77.382.542,97 |
| Reference         | 47.054.511,43 | 71.528.257,84 | 95.169.098,95 |
| Reference Random  | 47.054.511,43 | 93.615.262,32 | 95.169.098,95 |
| Reference Optimos | 47.409.540,37 | 71.528.257,84 | 77.504.818,50 |
| SA                | 47.433.718,09 | 73.779.573,57 | 78.350.481,99 |
| Tabu Search       | 47.409.540,37 | 71.528.257,84 | 77.504.818,50 |
| PPO               | 45.437.286,89 | 85.317.002,71 | 79.791.185,01 |
| Tabu Random       | 47.054.511,43 | 75.073.704,05 | 77.983.503,98 |
| SA Random         | 47.241.669,76 | 93.615.262,32 | 95.169.098,95 |
| PPO Random        | 46.879.543,35 | 71.455.570,34 | 77.905.095,08 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Sepsis_Das_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Sepsis_Das_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Sepsis_Das_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  4821 |                  7 |                              |        4.88522e+07 |    4.54373e+07 |            2.65374 |             4830 |        8.7928 | 716min<br/>(for 4821 Steps) |
| Proximal Policy Optimization Random |  2839 |                 18 |                              |        4.88577e+07 |    4.68795e+07 |            2.28247 |             2849 |       10.2445 | 445min<br/>(for 2839 Steps) |
| Simulated Annealing                 |    81 |                  1 |                           69 |        4.98798e+07 |    4.98798e+07 |             2.1224 |                4 |     0.0010123 | 1min<br/>(for 81 Steps)     |
| Simulated Annealing Random          |  2622 |               1180 |                         1008 |         5.0022e+07 |    4.72417e+07 |            3.66416 |              868 |      0.631759 | 280min<br/>(for 2622 Steps) |
| Tabu Search                         |   101 |                  1 |                           30 |        4.93868e+07 |    4.81111e+07 |            2.46034 |                5 |    0.00157211 | 1min<br/>(for 101 Steps)    |
| Tabu Search Random                  |  2501 |               1126 |                         1136 |        4.91912e+07 |    4.70545e+07 |            2.37901 |              830 |       6.26755 | 298min<br/>(for 2501 Steps) |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Sepsis_Das_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Sepsis_Das_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Sepsis_Das_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  2945 |                  9 |                              |        8.00567e+07 |    7.97912e+07 |            2.32697 |             2955 |       7.66747 | 403min<br/>(for 2945 Steps) |
| Proximal Policy Optimization Random |  3855 |                 15 |                              |        7.93788e+07 |    7.79051e+07 |            2.81407 |             3865 |       9.76478 | 510min<br/>(for 3855 Steps) |
| Simulated Annealing                 |   131 |                  2 |                          114 |        7.80104e+07 |    7.74798e+07 |            2.10698 |                7 |     0.0012939 | 2min<br/>(for 131 Steps)    |
| Simulated Annealing Random          |  2231 |                926 |                           36 |        1.16187e+08 |    9.51691e+07 |            3.42619 |              740 |       6.37437 | 297min<br/>(for 2231 Steps) |
| Tabu Search                         |   121 |                  1 |                           20 |        8.00764e+07 |    7.80771e+07 |             2.1309 |                6 |    0.00122361 | 2min<br/>(for 121 Steps)    |
| Tabu Search Random                  |    17 |                  1 |                            0 |        7.79835e+07 |    7.79835e+07 |            2.11549 |                3 |       3.10532 | 0min<br/>(for 17 Steps)     |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Sepsis_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Sepsis_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Sepsis_Das_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Sepsis_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Sepsis_Das_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Sepsis_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Sepsis_Das_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  5207 |                 20 |                              |        9.44429e+07 |     8.5317e+07 |            2.51837 |             5217 |        8.0266 | 705min<br/>(for 5207 Steps) |
| Proximal Policy Optimization Random |  5231 |                 47 |                              |        7.47033e+07 |    7.14556e+07 |            2.55251 |             5240 |       8.67956 | 717min<br/>(for 5231 Steps) |
| Simulated Annealing                 |   141 |                  2 |                          152 |         7.4814e+07 |     7.4814e+07 |             2.7255 |                8 |       2.00736 | 2min<br/>(for 141 Steps)    |
| Simulated Annealing Random          |  2402 |               1045 |                            0 |        1.00127e+08 |    9.36153e+07 |            3.30269 |              798 |      0.234691 | 293min<br/>(for 2402 Steps) |
| Tabu Search                         |   121 |                  1 |                           18 |        7.27851e+07 |    7.11963e+07 |            2.30249 |                6 |     0.0011708 | 2min<br/>(for 121 Steps)    |
| Tabu Search Random                  |    29 |                  4 |                            0 |        7.50737e+07 |    7.50737e+07 |            3.06194 |                7 |       5.81616 | 1min<br/>(for 29 Steps)     |

##### Pareto Front Images

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

---

### Trafic Das

#### Analyzer Overview

##### Pareto Size

| Agent / Reference | Easy  | Mid   | Hard  |
| ----------------- | ----- | ----- | ----- |
| Reference         | 10,00 | 16,00 | 22,00 |
| Reference Random  | 8,00  | 15,00 | 22,00 |
| Reference Optimos | 5,00  | 15,00 | 32,00 |
| SA                | 7,00  | 3,00  | 9,00  |
| Tabu Search       | 4,00  | 6,00  | 5,00  |
| PPO               | 5,00  | 17,00 | 29,00 |
| Tabu Random       | 5,00  | 15,00 | 6,00  |
| SA Random         | 4,00  | 3,00  | 6,00  |
| PPO Random        | 8,00  | 15,00 | 22,00 |

<br>

##### Hyperarea Ratio

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,00 | 1,00 | 1,00 |
| Reference Optimos | 1,00 | 1,00 | 1,00 |
| SA                | 0,93 | 0,96 | 1,00 |
| Tabu Search       | 0,94 | 0,97 | 1,00 |
| PPO               | 1,00 | 1,00 | 1,00 |
| Tabu Random       | 0,97 | 0,99 | 1,00 |
| SA Random         | 0,96 | 1,00 | 1,00 |
| PPO Random        | 1,00 | 1,00 | 1,00 |

<br>

##### Hausdorff

| Agent / Reference | Easy       | Mid        | Hard         |
| ----------------- | ---------- | ---------- | ------------ |
| Reference Random  | 30.622,38  | 21.885,52  | 0,00         |
| Reference Optimos | 13.820,94  | 227.175,14 | 148.348,66   |
| SA                | 109.147,00 | 248.862,10 | 309.816,74   |
| Tabu Search       | 110.960,66 | 237.025,86 | 469.460,00   |
| PPO               | 13.820,94  | 227.175,14 | 198.400,91   |
| Tabu Random       | 108.571,56 | 114.943,76 | 1.203.658,64 |
| SA Random         | 110.626,92 | 96.732,90  | 331.225,12   |
| PPO Random        | 30.622,38  | 47.134,59  | 166.156,72   |

<br>

##### Delta

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 1,51 | 1,01 | 0,97 |
| Reference Optimos | 1,40 | 1,33 | 0,88 |
| SA                | 0,81 | 0,98 | 1,27 |
| Tabu Search       | 0,90 | 0,93 | 0,95 |
| PPO               | 1,40 | 1,33 | 0,85 |
| Tabu Random       | 0,79 | 0,98 | 1,22 |
| SA Random         | 0,83 | 0,50 | 0,91 |
| PPO Random        | 1,51 | 1,01 | 0,80 |

<br>

##### Purity

| Agent / Reference | Easy | Mid  | Hard |
| ----------------- | ---- | ---- | ---- |
| Reference Random  | 0,70 | 0,31 | 1,00 |
| Reference Optimos | 0,30 | 0,69 | 0,00 |
| SA                | 0,00 | 0,00 | 0,00 |
| Tabu Search       | 0,00 | 0,00 | 0,00 |
| PPO               | 0,30 | 0,69 | 0,00 |
| Tabu Random       | 0,00 | 0,00 | 0,23 |
| SA Random         | 0,00 | 0,12 | 0,05 |
| PPO Random        | 0,70 | 0,19 | 0,73 |

<br>

##### Avg Cycle Time

| Agent / Reference | Easy         | Mid           | Hard          |
| ----------------- | ------------ | ------------- | ------------- |
| Base              | 4.406.883,21 | 4.237.002,88  | 4.235.563,50  |
| Reference         | 1.245.508,53 | 3.236.511,47  | 11.249.272,88 |
| Reference Random  | 832.853,83   | 3.020.570,10  | 11.249.272,88 |
| Reference Optimos | 2.558.990,90 | 12.385.577,44 | 11.269.135,07 |
| SA                | 2.334.547,68 | 4.668.437,81  | 60.213.221,47 |
| Tabu Search       | 2.324.422,20 | 10.161.927,77 | 4.546.275,16  |
| PPO               | 2.558.990,90 | 12.385.577,44 | 12.641.990,69 |
| Tabu Random       | 1.781.635,13 | 15.554.223,59 | 54.923.323,88 |
| SA Random         | 2.594.287,50 | 6.540.162,08  | 19.816.682,85 |
| PPO Random        | 832.853,83   | 3.400.742,03  | 11.422.093,12 |

<br>

##### Best Cycle Time

| Agent / Reference | Easy         | Mid          | Hard         |
| ----------------- | ------------ | ------------ | ------------ |
| Base              | 4.406.883,21 | 4.237.002,88 | 4.235.563,50 |
| Reference         | 89.304,46    | 520.078,31   | 2.594.306,70 |
| Reference Random  | 89.304,46    | 520.078,31   | 2.594.306,70 |
| Reference Optimos | 607.541,34   | 1.471.187,97 | 3.890.929,73 |
| SA                | 1.469.943,01 | 4.150.208,86 | 3.890.929,73 |
| Tabu Search       | 1.903.540,02 | 5.703.105,99 | 4.147.636,37 |
| PPO               | 607.541,34   | 1.471.187,97 | 4.235.563,50 |
| Tabu Random       | 866.616,18   | 1.471.969,73 | 2.940.590,48 |
| SA Random         | 1.730.491,24 | 520.078,31   | 2.594.306,70 |
| PPO Random        | 89.304,46    | 1.298.623,46 | 4.235.563,50 |

<br>

#### Easy

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Easy_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Easy_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Trafic_Das_Easy_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Easy_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Trafic_Das_Easy_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Easy_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Trafic_Das_Easy_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  4808 |                136 |                              |        2.55899e+06 |         607541 |            21.3091 |             4818 |       5.81425 | 415min<br/>(for 4808 Steps) |
| Proximal Policy Optimization Random |  6224 |                414 |                              |             832854 |        89304.5 |            6.77143 |             6234 |       5.06246 | 427min<br/>(for 6224 Steps) |
| Simulated Annealing                 |  9992 |                427 |                         2248 |        2.33455e+06 |    1.46994e+06 |            2.56383 |              577 |       4.71075 | 119min<br/>(for 9992 Steps) |
| Simulated Annealing Random          |  2614 |               1327 |                          243 |        2.59429e+06 |    1.73049e+06 |            3.97904 |              868 |       4.64431 | 186min<br/>(for 2614 Steps) |
| Tabu Search                         |  7057 |                216 |                         3412 |        2.31422e+06 |    1.90354e+06 |            3.61417 |              485 |       2.00739 | 101min<br/>(for 7057 Steps) |
| Tabu Search Random                  |  2615 |               1405 |                          383 |        1.78164e+06 |         866616 |            4.03289 |              868 |       2.71143 | 153min<br/>(for 2615 Steps) |

##### Pareto Front Images

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

#### Hard

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Hard_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Hard_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Trafic_Das_Hard_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Hard_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Trafic_Das_Hard_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Hard_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Trafic_Das_Hard_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  1581 |                 44 |                              |        1.23984e+07 |    3.63188e+06 |            7.29797 |             1590 |         46.16 | 712min<br/>(for 1581 Steps) |
| Proximal Policy Optimization Random |  3811 |                280 |                              |        1.14576e+07 |    8.03874e+06 |            9.57933 |             3820 |       12.2776 | 716min<br/>(for 3811 Steps) |
| Simulated Annealing                 |  9997 |                573 |                          773 |        6.02035e+07 |    3.89093e+06 |            2.17771 |              598 |      0.238621 | 142min<br/>(for 9997 Steps) |
| Simulated Annealing Random          |  2581 |               1185 |                          165 |        3.05005e+07 |    2.59431e+06 |            2.08344 |              857 |       5.73251 | 298min<br/>(for 2581 Steps) |
| Tabu Search                         |  2977 |                181 |                         1214 |        4.54628e+06 |    4.14764e+06 |            2.01762 |              186 |     0.0343043 | 47min<br/>(for 2977 Steps)  |
| Tabu Search Random                  |  1286 |                600 |                            0 |        5.49233e+07 |    2.94059e+06 |                2.5 |              426 |       3.56618 | 184min<br/>(for 1286 Steps) |

##### Pareto Front Images

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

#### Mid

##### Metric Plots

<table>
<tr><td><strong>Pareto Front Size</strong><br><img src='report_plots/Trafic_Das_Mid_front_size.png' alt='Pareto Front Size' style='width:300px;height:200px;'/></td><td><strong>Explored Solutions</strong><br><img src='report_plots/Trafic_Das_Mid_global_solutions_tried.png' alt='Explored Solutions' style='width:300px;height:200px;'/></td><td><strong>Potential New Base Solutions</strong><br><img src='report_plots/Trafic_Das_Mid_base_solutions.png' alt='Potential New Base Solutions' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Average Cycle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_avg_cycle_time.png' alt='Average Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Min Cycle Time</strong><br><img src='report_plots/Trafic_Das_Mid_front_min_cycle_time.png' alt='Min Cycle Time' style='width:300px;height:200px;'/></td><td><strong>Average Batch Size</strong><br><img src='report_plots/Trafic_Das_Mid_current_base_average_batch_size.png' alt='Average Batch Size' style='width:300px;height:200px;'/></td></tr>
<tr><td><strong>Iteration Number</strong><br><img src='report_plots/Trafic_Das_Mid_global_iteration.png' alt='Iteration Number' style='width:300px;height:200px;'/></td><td><strong>Time per Step</strong><br><img src='report_plots/Trafic_Das_Mid_time_per_step.png' alt='Time per Step' style='width:300px;height:200px;'/></td><td></td></tr>
</table>

##### Summary Table (Final Values)

| Agent                               | Steps | Explored Solutions | Potential New Base Solutions | Average Cycle Time | Min Cycle Time | Average Batch Size | Iteration Number | Time per Step | Total Optimization Time     |
| :---------------------------------- | ----: | -----------------: | ---------------------------: | -----------------: | -------------: | -----------------: | ---------------: | ------------: | :-------------------------- |
| Proximal Policy Optimization        |  8001 |                170 |                              |        1.15895e+07 |    1.47119e+06 |            3.97139 |             8010 |       5.28506 | 717min<br/>(for 8001 Steps) |
| Proximal Policy Optimization Random |  7171 |                146 |                              |        3.52303e+06 |    1.29862e+06 |            49.9739 |             7180 |       5.20373 | 717min<br/>(for 7171 Steps) |
| Simulated Annealing                 |  9998 |                522 |                         1045 |        4.66844e+06 |    4.15021e+06 |            2.02184 |              573 |      0.437328 | 197min<br/>(for 9998 Steps) |
| Simulated Annealing Random          |  2614 |               1160 |                          119 |        6.54016e+06 |         520078 |              2.102 |              868 |       6.59526 | 258min<br/>(for 2614 Steps) |
| Tabu Search                         |  5098 |                229 |                         2118 |        1.15793e+07 |    5.70311e+06 |            2.95782 |              276 |      0.121986 | 61min<br/>(for 5098 Steps)  |
| Tabu Search Random                  |  2615 |               1306 |                          723 |        1.55542e+07 |    1.47197e+06 |            3.90977 |              868 |       4.81121 | 188min<br/>(for 2615 Steps) |

##### Pareto Front Images

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
