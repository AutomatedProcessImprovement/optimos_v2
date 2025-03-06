import os
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Literal, Optional, Union

from o2.models.legacy_approach import LegacyApproach


class AgentType(Enum):
    """The type of agent to use for the optimization task."""

    TABU_SEARCH = "tabu_search"
    SIMULATED_ANNEALING = "simulated_annealing"
    PROXIMAL_POLICY_OPTIMIZATION = "proximal_policy_optimization"
    TABU_SEARCH_RANDOM = "tabu_search_random"
    SIMULATED_ANNEALING_RANDOM = "simulated_annealing_random"
    PROXIMAL_POLICY_OPTIMIZATION_RANDOM = "proximal_policy_optimization_random"


class CostType(Enum):
    """The type of cost to use for the optimization task."""

    TOTAL_COST = "total_cost"
    """The total cost, including fixed costs per task / batch
    and resource costs (e.g. hourly wages)."""

    RESOURCE_COST = "resource_cost"
    """The resource cost, excluding fixed costs per task / batch."""

    FIXED_COST = "fixed_cost"
    """The fixed cost per task / batch. No resource costs."""

    WAITING_TIME_AND_PROCESSING_TIME = "wt_pt"
    """Instead of using an financial cost use
    waiting time (incl. idle time) and processing time"""

    AVG_WT_AND_PT_PER_TASK_INSTANCE = "avg_wt_pt_per_task_instance"
    """Instead of using an financial cost use average
    waiting time (incl. idle time) and processing time per task instance"""


@dataclass()
class Settings:
    """Settings for the Optimos v2 application.

    This class is initialized with sensible defaults, but can be changed to
    suit the needs of the user, e.g. to run it in legacy optimos mode.
    """

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

    batching_only = False
    """Should only batching rules be optimized?"""

    only_allow_low_last = False
    """Should `low` rated Actions be tried last?

    E.g. ONLY if no other/higher Action is available.
    """

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    legacy_approach: LegacyApproach = LegacyApproach.CALENDAR_FIRST
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
    """The max distance to the new base solution to be considered for TABU evaluation.
    With distance being the min euclidean distance to any solution in
    the current Pareto Front.

    NOTE: This is an absolute number. You most likely want to use
    error_radius_in_percent instead, to limit the distance to the new base solution.
    """

    never_select_new_base_solution = False
    """Disables the logic to automatically select a new base solution.

    This is useful if you want to go greedy without backing off to a previous
    base solution.E.g. in the PPO Training.
    """

    error_radius_in_percent: Optional[float] = 0.05
    """This is the "error" for the hill climbing agent to still consider a solution.

    Also this will be used to calculate the sa_cooling_factor if this is set to "auto".

    When set the Tabu-Search will behave similar to what is commonly called hill climbing.
    (Even though a Tabu-List is still maintained)
    """

    sa_cooling_factor: Union[float, Literal["auto"]] = "auto"
    """The cooling factor for the simulated annealing agent.

    It's a float between 0 and 1 that will be multiplied with the temperature
    every iteration. If this is set to "auto", the cooling factor will be
    calculated so that after sa_cooling_iteration_percent the
    temperature will be error_radius_in_percent
    """

    sa_cooling_iteration_percent = 0.80
    """Percentage of iterations after which the SA should basically be hill climbing.

    This is only relveant if sa_cooling_factor is set to "auto".
    NOTE: Reaching this threshold will not stop the cooling process. 
    It's only used to calculate the cooling factor.
    """

    sa_initial_temperature: Union[float, Literal["auto"]] = "auto"
    """The initial temperature for the simulated annealing agent."""

    ppo_model_path = "models/ppo_maskable-20241025-075307"
    """The path to the PPO model to use for the PPO agent."""

    ppo_use_existing_model = False
    """Should the PPO agent use an existing model?"""

    ppo_steps_per_iteration = 50
    """The number of steps per iteration for the PPO agent."""

    log_to_tensor_board = False
    """Should the evaluation be logged to TensorBoard?"""

    throw_on_iteration_errors = False
    """Should the application throw an error if an iteration fails?

    Useful for debugging, but should be disabled for production.
    """

    MAX_YIELDS_PER_ACTION: ClassVar[Optional[int]] = None
    """The maximum number of yields per action.

    This can be used esp. in many-task/many-resource scenarios, where
    the number of possible actions is very high. In this case the optimizer will only consider
    the best X actions.
    """

    ADD_SIZE_RULE_TO_NEW_RULES: ClassVar[bool] = True
    """Should a size rule be added to new rules?

    This is esp. relevant for date time rules, as it allows the optimizer,
    very easily to later increase / decrease it. But as Prosimos isn't quite
    behaving the same with a size rule, this may be disabled by the user.
    """

    SHOW_SIMULATION_ERRORS: ClassVar[bool] = False
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """

    RAISE_SIMULATION_ERRORS: ClassVar[bool] = False
    """Should the simulation errors be raised?

    This is useful for debugging, but should be disabled for production.
    """

    DUMP_DISCARDED_SOLUTIONS: ClassVar[bool] = False
    """Should the solutions be dumped (to file system via pickle) after they have been dominated?

    This should only be activated for evaluation, as it will cause IO & processing overhead.
    """

    COST_TYPE: ClassVar[CostType] = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    """The type of cost to use for the optimization task.

    Because this won't differ during the optimization, it's a class variable.
    """

    NUMBER_OF_CASES: Optional[int] = None
    """Overrite the number of cases to simulate per run.

    Will use information from the model if not set (1000 cases by default)."""

    EQUAL_DOMINATION_ALLOWED: ClassVar[bool] = False
    """Should equal domination be allowed?

    If this is set to True, the pareto front will allow solutions with the same
    x and y values.
    """

    LOG_LEVEL: ClassVar[str] = "DEBUG"
    """The log level to use for the application."""

    LOG_FILE: ClassVar[Optional[str]] = None
    """The log file to use for the application."""

    ARCHIVE_TENSORBOARD_LOGS: ClassVar[bool] = True
    """Should the tensorboard logs be archived?

    This is useful to collect logs from multiple runs, but if the runs are
    run parallel, it might interfere with the runs.
    """

    ARCHIVE_SOLUTIONS: ClassVar[bool] = False
    """Should the solutions' evaluations and states be archived?

    This is useful for large models, because keeping all solutions in memory
    might cause memory issues. When enabled, the solutions will be archived
    to the file system via pickle and loaded on demand.
    """

    DELETE_LOADED_SOLUTION_ARCHIVES: ClassVar[bool] = True
    """If an archived solution is loaded, should it be deleted?

    This will save (some) disk space, but will be slower, as a solution might
    need to be delted & rewritten to disk multiple times.
    """

    OVERWRITE_EXISTING_SOLUTION_ARCHIVES: ClassVar[bool] = True
    """If an archived solution is loaded, should it be overwritten?

    This will save (some) disk space, but will be slower, as a solution might
    need to be delted & rewritten to disk multiple times.
    """

    CHECK_FOR_TIMETABLE_EQUALITY: ClassVar[bool] = False
    """Should the equality of timetables be checked when comparing solutions?

    This includes unordered comparison of firing rules.

    This should be enabled for analysis, but might be to slow for actual
    optimization runs.
    """

    @staticmethod
    def get_pareto_x_label() -> str:
        """Get the label for the x-axis (cost) of the pareto front."""
        if Settings.COST_TYPE == CostType.WAITING_TIME_AND_PROCESSING_TIME:
            return "Processing Time"
        elif Settings.COST_TYPE == CostType.FIXED_COST:
            return "Fixed Cost"
        elif Settings.COST_TYPE == CostType.RESOURCE_COST:
            return "Resource Cost"
        elif Settings.COST_TYPE == CostType.TOTAL_COST:
            return "Total Cost"
        elif Settings.COST_TYPE == CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE:
            return "Batch Processing per Task"
        else:
            raise ValueError(f"Unknown cost type: {Settings.COST_TYPE}")

    @staticmethod
    def get_pareto_y_label() -> str:
        """Get the label for the y-axis (duration) of the pareto front."""
        if Settings.COST_TYPE == CostType.WAITING_TIME_AND_PROCESSING_TIME:
            return "Waiting Time"
        elif Settings.COST_TYPE == CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE:
            return "WT-Idle per Task"
        else:
            return "Total Duration"
