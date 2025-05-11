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


class ActionVariationSelection(Enum):
    """The method to use for selecting action variations."""

    SINGLE_RANDOM = "single_random"
    """Select a single random rule"""

    FIRST_IN_ORDER = "first_in_order"
    """Select the first rule in the list"""

    FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER = "first_max_variants_per_action_in_order"
    """Select the max_variants_per_action first rules in the list

    E.g. if max_variants_per_action=3 you will get the first 3 rules.
    NOTE: For inner loops this will only pick 1 rule, so that the constraints are not broken.
    """

    RANDOM_MAX_VARIANTS_PER_ACTION = "random_max_variants_per_action"
    """Select a random rule, but only consider the best max_variants_per_action rules

    NOTE: For inner loops this will only pick 1 rule, so that the constraints are not broken.
    """

    ALL_RANDOM = "all_random"
    """Select all rules randomly"""

    ALL_IN_ORDER = "all_in_order"
    """Select all rules in order"""

    @property
    def ordered(self) -> "ActionVariationSelection":
        """Return the selection enum, that should be used for ordered selection.

        This is used, when the action variations are already ordered, so random selection is not needed.
        Meaning: For random selection, this will return the enum with non-random selection.
        For the other cases, it will return the same enum.
        """
        if self == ActionVariationSelection.SINGLE_RANDOM:
            return ActionVariationSelection.FIRST_IN_ORDER
        elif self == ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION:
            return ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
        elif self == ActionVariationSelection.ALL_RANDOM:
            return ActionVariationSelection.ALL_IN_ORDER
        else:
            return self

    @property
    def inner(self) -> "ActionVariationSelection":
        """Return the selection enum, that should be used for inner selection.

        This is used in the inner loop, where we only want to select one rule.
        Meaning: For multi-selection, this will return the enum with single selection.
        For single selection, it will return the same enum.
        """
        if self == ActionVariationSelection.ALL_IN_ORDER:
            return ActionVariationSelection.FIRST_IN_ORDER
        elif self == ActionVariationSelection.ALL_RANDOM:
            return ActionVariationSelection.SINGLE_RANDOM
        elif self == ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER:
            return ActionVariationSelection.FIRST_IN_ORDER
        elif self == ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION:
            return ActionVariationSelection.SINGLE_RANDOM
        else:
            return self

    @property
    def infinite_max_variants(self) -> "ActionVariationSelection":
        """Choice if the max variants is infinite."""
        if self == ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER:
            return ActionVariationSelection.ALL_IN_ORDER
        elif self == ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION:
            return ActionVariationSelection.ALL_RANDOM
        else:
            return self


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

    iterations_per_solution: Optional[int] = None
    """The number of iterations to run for each base solution.

    If this is set, the optimizer will run for this number of iterations for each
    base solution, before selecting a new one. If this is not set, the optimizer
    will run until the max_iterations is reached.
    """

    max_iterations = 1000
    """The maximum (total) number of iterations before the application stops."""

    max_solutions: Optional[int] = None
    """The maximum number of solutions to evaluate.

    If this is set, the optimizer will stop after this number of solutions has been evaluated.
    Often, rather then setting this, it's better to set max_iterations.
    """

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
    - In this case calendar optimizations will get a higher priority,
      the resource optimizations will get a "low" priority, that will only(!)
      be executed after the calendar optimization
    - Then as soon as one of the calendar optimizations is successful,
      we switch this setting to resources first, so that the resources
      are optimized first, and the calendar is optimized afterwards.
    """

    max_number_of_actions_per_iteration = os.cpu_count() or 1
    """The maximum number of actions to select for for (parallel) evaluation."""

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

    error_radius_in_percent: Optional[float] = 0.02
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

    sa_cooling_iteration_percent = 0.55
    """Percentage of iterations after which the SA should basically be hill climbing.

    This is only relevant if sa_cooling_factor is set to "auto".
    NOTE: Reaching this threshold will not stop the cooling process.
    It's only used to calculate the cooling factor.
    """

    sa_initial_temperature: Union[float, Literal["auto"]] = "auto"
    """The initial temperature for the simulated annealing agent."""

    sa_strict_ordered = False
    """Should the SA agent be strict ordered?

    If this is set to True, the SA agent will take solutions in temperature range ordered by their distance
    to the current pareto front (Similar to the hill climbing approach). This is not strictly SA, because that
    would require a random selection of the solutions, but it will speed up the optimization.

    Also setting this to True will disable the random acceptance of a bad solutions.
    """

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

    disable_action_validity_check = False
    """Disables the logic to check if actions produces sensible results, before actually evaluating them.

    This is used by the Random Agents, as they should be able to select any action,
    even if it's not valid. (The validity check is considered to be part of the metrics)
    """

    action_variation_selection: ActionVariationSelection = ActionVariationSelection.ALL_IN_ORDER
    """The method to use for selecting action variations.

    Context:
    Actions usually have a sorted component and then an options component.
    E.g. the ModifySizeRuleByCostAction will first select the task with the highest cost,
    and then get a list of all size rules for that task. Now the question is, how to select
    the rule(s) which should be modified (the "variants"). This setting will set the method how to select
    the variant(s).

    See the ActionVariationSelection and max_variants_per_action for more details.
    """

    max_variants_per_action: Optional[int] = None
    """The maximum number of variants per action.

    This can be used esp. in many-task/many-resource scenarios, where
    the number of possible actions is very high. It limits the number of variants
    per action. With a variant being a specific sub-setting of an action, e.g. a specific
    size rule or a specific resource for a task.

    NOTE: This number is _not_ per iteration, but per base_solution.
    """

    override_action_variation_selection_for_inner_loop: bool = False
    """Should the `inner` parameter of the action variation selection be ignored?

    Only activate if you know what you are doing!

    It's useful if you want to force the optimizer to output EVERY variant.
    Usually this is not needed, as we can rely on randomness,e.g via `ActionVariationSelection.ALL_RANDOM`,
    but if you want a deterministic output, you can set this to True (E.g. for testing).
    """

    DISABLE_PARALLEL_EVALUATION: ClassVar[bool] = False
    """Should the parallel evaluation be disabled? This is useful for debugging.

    This will override any MAX_THREADS_ACTION_EVALUATION/MAX_THREADS_MEDIAN_CALCULATION settings.
    """

    MAX_THREADS_ACTION_EVALUATION: ClassVar[int] = os.cpu_count() or 1
    """The maximum number of threads to use for parallel evaluation
    of actions."""

    MAX_THREADS_MEDIAN_CALCULATION: ClassVar[int] = 1
    """The maximum number of threads to use for parallel median calculation.

    If you are already using parallel evaluation of actions, you might want to keep this at 1,
    not to have to much processes running at the same time.
    """

    MAX_YIELDS_PER_ACTION: ClassVar[Optional[int]] = None
    """The maximum number of yields per action.

    This will be enforced even over multiple iterations (as long as the base_solution
    is not changed). Usually it doesn't make sense to set this, as the number of solutions can be controlled
    by the max_number_of_actions_per_iteration.
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
    """Override the number of cases to simulate per run.

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
    need to be deleted & rewritten to disk multiple times.
    """

    OVERWRITE_EXISTING_SOLUTION_ARCHIVES: ClassVar[bool] = True
    """If an archived solution is loaded, should it be overwritten?

    This will save (some) disk space, but will be slower, as a solution might
    need to be deleted & rewritten to disk multiple times.
    """

    CHECK_FOR_TIMETABLE_EQUALITY: ClassVar[bool] = False
    """Should the equality of timetables be checked when comparing solutions?

    This includes unordered comparison of firing rules.

    This should be enabled for analysis, but might be to slow for actual
    optimization runs.
    """

    DISABLE_REMOVE_ACTION_RULE: ClassVar[bool] = True
    """Should the remove action rule be disabled?

    Theoretically it doesn't make sense to remove an firing rule, as it was
    added at some point, so the evaluation without that action should have been
    done already.

    But in practice it might make sense to disable this, as it might help the
    optimizer to find a better solution.
    """

    NUMBER_OF_SIMULATION_FOR_MEDIAN: ClassVar[int] = 5
    """The number of simulations to run for each new state.

    Because of simulation variation/error, we run multiple simulations and take the median.
    It's recommended to set this to an odd number, to avoid ties.
    """

    USE_MEDIAN_SIMULATION_FOR_EVALUATION: ClassVar[bool] = True
    """Should the median simulation be used for evaluation?

    Because of simulation variation/error, it's recommended to run multiple
    simulations and take the median. (See NUMBER_OF_SIMULATION_FOR_MEDIAN for more details)
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
