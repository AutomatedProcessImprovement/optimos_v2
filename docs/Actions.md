# Actions

## General Note

OptimosV2 follows a _State-Action-Reducer-Pattern_. Meaning: There is a immutable **state**, that is the current solutions, actions are parameters that describe a change to the state, and a **reducer** that applies the change to the state, returning a copy. A **Store** manages the state and the actions.

**Action**: An Action is just a description of a change to the state (e.g. "Add a Weekday Batching Rule"). It contains parameters, e.g. which day to add.

**Actions parameters**: Action Options themselves are modeled in the form of Parameter-Classes (e.g. `AddWeekDayRuleActionParams` ).

**Reducers**: To keep all the Logic in one place, and opposite to e.g. _Flux_, the Action also contains the logic to apply the change to the state and return a new immutable copy (usually called a **"Reducer"**). This is done in static the `apply` method.

**Action Creation Generator**: Additionally the Logic for creating the Action is also in the Action-Class (usually called an **"Action Creator"**). This is done via the `rate_self` generator. Using a generator has the great advantage that one ActionCreator might yield many action, either if the ActionSelector has not yet found enough actions, to fill up the cpu cores of the host machine, or if a previous action was already tried and is in the tabu list.

This allows us the try the seemingly second-best action, e.g. together, with the best action, and maybe the second best action performs actually better.

**On Rating**: Another important change to the Flux-Pattern is that each action created by the `rate_self`-generator has a **self-rating**, e.g. how good the generator thinks the action is. Some Actions are very radical, e.g. remove a batching rule all together, it has a very low self-rating, so it will only be tried if no other action is available.

**Store**: Last but not least, similarly to flux, OptimosV2 also has a store that manages the state and the actions.

## Implemented

### Batching

#### AddWeekDayRuleAction

- **What?** Clones an existing Weekday Batching Rule and adds it for a new Weekday
- **When?** Get the most impactful rules desc, if one is a Weekday Batching Rule, clone it and add it for a new Weekday
- **Self-Rating**: Constant, Medium

#### ModifyDailyHourRuleAction

- **What?** Shifts the time of a Daily Hour Rule
- **When?** Looks at the rules that increased the WT the most, and the one that decreased it the most,
  If one of them is a DailyHourRule, move the time of the rule.
- **Self-Rating**: Constant, Medium

#### ModifyLargeWtRuleAction

- **What?** Reduces the WT threshold for a LargeWT Rule
- **When?** Looks at the rules that changed the WT the most. If one is a LargeWT Rule, reduce the threshold
- **Self-Rating**: Constant, Medium

#### ModifyReadyWtRuleAction

- **What?** Reduces the WT threshold for a ReadyWT Rule
- **When?** Looks at the rules that changed the WT the most. If one is a ReadyWT Rule, reduce the threshold
- **Self-Rating**: Constant, Medium

#### ModifySizeRuleAction

- **What?** Modifies the batching size threshold for a SizeRule
- **When?** Looks at the rules that changed the WT the most. If one is a SizeRule, if it increased the WT,
  reduce the size threshold, else increase it.
- **Self-Rating**: Constant, Medium

### RemoveRuleAction

- **What?** Removes any Firing Rule
- **When?** Looks at the rules that increased the WT the most. Try to remove it.
- **Self-Rating**: Constant, Low -- Only if no other action is available

### Calendar (Legacy Optimos)

#### ModifyCalendarByCostAction

- **What?** Modifies the resource calendar by shrinking/shifting the working time
- **When?** It will fist iterate over all resources sorted by their
  cost (cost/hour \* available_time), for each resource it will iterate over
  each day in their calendar. For each day it will try to modify the
  first period (shift), by either removing it (if it's only 1 hour long),
  shrinking it from start & end, shrinking it from the start,
  or finally shrinking it from the end.

#### ModifyCalendarByIdleTimeAction

- **What?** Modifies the resource calendar by adding working time at the end of shifts
- **When?** It will first find the tasks with the most idle time, then find the days where
  those are executed the most, and then find the resources
  that does this task the most. (Although not for that day, as it was in Optimos).
  Then it will look at the resource calendars for those resources on those days,
  and first try to add hours to the end of the shifts, and if that is not possible,
  it will try to shift the shifts to start later. Finally it will try to add hours
  to be beginning & start of the shift.

#### ModifyCalendarByWaitingTimeAction

- **What?** Modifies the resource calendar by adding working time at the start of shifts
- **When?** It will first find the tasks with the most waiting time, then find the days where
  those are executed the most, and then find the resources
  that does this task the most. (Although not for that day, as it was in Optimos).
  Then it will look at the resource calendars for those resources on those days,
  and first try to add hours to the start of the shifts, and if that is not possible,
  it will try to shift the shifts to start earlier.

### Resource (Legacy Optimos)

#### ModifyResourceByCostAction

- **What?** Removes the most costly resource
- **When?** It first gets all resources sorted by their cost (cost/hour \* available_time),
  then it removes the resource with the highest cost, if that resource's tasks
  can be done by other resources.

#### ModifyResourceByUtilizationAction

- **What?** Removes the least utilized resource
- **When?** It first gets all resources sorted by their utilization (ascending)
  then it removes the resource with the lowest utilization, if that resource's tasks
  can be done by other resources.

## Action ToDos

#### Add Rule Action

- **What?** Adds a Batching Rule based on the constraints
- **When?** ???
