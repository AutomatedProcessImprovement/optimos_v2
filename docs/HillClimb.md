# HillClimb

### How does Optimos decide if a evaluated action is good or bad?

Optimos uses a pareto front, to decide if an action is good or bad. The pareto front is a set of actions that are not dominated by any other action. An action is dominated by another action if the other action is better in all dimensions (see below).

### Dimensions in the Pareto Front

1. Total Cycle Time of all cases of the simulation
2. Total Cost of all cases of the simulation. With cost being the sum of the cost of all resources, and the cost of a resource being the time available multiplied by the cost per hour. A Resource is available if a working hour is scheduled in it's calendar.
