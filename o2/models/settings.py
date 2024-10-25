import os
from dataclasses import dataclass
from enum import Enum

from o2.models.legacy_approach import LegacyApproach


class AgentType(Enum):
    """The type of agent to use for the optimization task."""

    TABU_SEARCH = "tabu_search"
    SIMULATED_ANNEALING = "simulated_annealing"
    PROXIMAL_POLICY_OPTIMIZATION = "proximal_policy_optimization"


@dataclass()
class Settings:
    """Settings for the Optimos v2 application.

    This class is initialized with sensible defaults, but can be changed to
    suit the needs of the user, e.g. to run it in legacy optimos mode.
    """

    num_of_cases = 100
    """The number of cases to simulate per run."""

    agent: AgentType = AgentType.TABU_SEARCH
    """The agent to use for the optimization task."""

    max_non_improving_actions = 1000
    """The maximum number of actions before discarding a base solution.

    Non-improving actions are all actions, which solutions are not dominating the
    current Pareto Front.
    """
    max_iterations = 1000
    """The maximum (total) number of iterations before the application stops."""

    optimos_legacy_mode = False
    """Should this application behave like an approximation of the original OPTIMOS?"""

    only_allow_low_last = True
    """Should `low` rated Actions be tried last?

    E.g. ONLY if no other/higher Action is available.
    """

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    show_simulation_errors = False
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """

    legacy_approach = LegacyApproach.CALENDAR_FIRST
    """
    This Setting is used to simulate different approaches used by legacy optimos.

    While _FIRST / _ONLY are self explanatory, the the _NEXT aka combined mode is a bit more complex.
    The combined mode is a mode where the calendar and resources are optimized at the same time.
    Legacy Optimos will first try calendar and then resources, if the calendar optimization
    finds a result, the resources are still optimized.

    To reproduce this in the new Optimos, we have to do the following:
    - We initialize the setting with calendar first,
    - In this case calendar optimizations will get a higher prio, 
      the resource optimizations will get a "low" prio, that will only(!)
      be executed after the calendar optimization
    - Then as soon as one of the calendar optimizations is successful, 
      we switch this setting to resources first, so that the resources
      are optimized first, and the calendar is optimized afterwards.
    """

    max_threads = os.cpu_count() or 1
    """The maximum number of threads to use for parallel evaluation."""

    max_number_of_actions_to_select = os.cpu_count() or 1
    """The maximum number of actions to select for for (parallel) evaluation."""

    disable_parallel_evaluation = False
    """Should the parallel evaluation be disabled? This is useful for debugging."""

    max_distance_to_new_base_solution = float("inf")
    """The maximum distance to the new base solution to be considered for evaluation.
    With distance being the min euclidean distance to any solution in
    the current Pareto Front.
    """

    never_select_new_base_solution = False
    """Disables the logic to automatically select a new base solution.

    This is useful if you want to go greedy without backing off to a previous
    base solution.E.g. in the PPO Training.
    """

    sa_cooling_factor = 0.90
    """The cooling factor for the simulated annealing agent."""

    sa_initial_temperature = 10_000_000_000
    """The initial temperature for the simulated annealing agent."""

    ppo_model_path = "models/ppo_maskable-20241025-075307"
    """The path to the PPO model to use for the PPO agent."""
