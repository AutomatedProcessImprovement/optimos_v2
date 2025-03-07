from dataclasses import replace

from o2.actions.batching_actions.modify_size_rule_by_cost_fn import (
    ModifyBatchSizeIfNoCostImprovement,
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnLowProcessingTime,
)
from o2.actions.batching_actions.modify_size_rule_by_utilization import ModifySizeRuleByHighUtilizationAction
from o2.actions.batching_actions.modify_size_rule_by_wt_action import ModifySizeRuleByWTAction
from o2.agents.tabu_agent import TabuAgent
from o2.models.rule_selector import RuleSelector
from o2.models.settings import ActionVariationSelection
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE, FiringRule
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_get_valid_actions_one_task(one_task_solution: Solution):
    """
    This test is to ensure that the different action selection settings are working as expected.
    """

    timetable = one_task_solution.state.timetable
    new_timetable = (
        timetable.add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 3),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 5),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 7),
        )
    )

    new_state = replace(one_task_solution.state, timetable=new_timetable)
    constraints = (
        ConstraintsGenerator(one_task_solution.state.bpmn_definition)
        .add_size_constraint(
            # For ModifyBatchSizeIfNoCostImprovement to propose a change,
            # we need to assume static costs
            cost_fn="1"
        )
        .constraints
    )

    store = Store.from_state_and_constraints(
        new_state,
        constraints,
    )

    store.settings.action_variation_selection = (
        ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    )
    store.settings.max_variants_per_action = 2
    store.settings.max_number_of_actions_per_iteration = 2
    store.settings.only_allow_low_last = False

    agent = TabuAgent(store)
    agent.catalog = [
        ModifySizeRuleByCostFnHighCosts,
        ModifyBatchSizeIfNoCostImprovement,
    ]
    agent.set_action_generators(store.solution)

    a1, a2 = agent.get_valid_actions()

    assert isinstance(a1[1], ModifySizeRuleByCostFnHighCosts)
    assert isinstance(a2[1], ModifyBatchSizeIfNoCostImprovement)

    assert a1[1].params["rule"].firing_rule_index == (0, 0)
    assert a2[1].params["rule"].firing_rule_index == (0, 0)
    assert a1[1].params["size_increment"] == 1
    assert a2[1].params["size_increment"] == -1

    a3, a4 = agent.get_valid_actions()

    assert isinstance(a3[1], ModifySizeRuleByCostFnHighCosts)
    assert isinstance(a4[1], ModifyBatchSizeIfNoCostImprovement)

    assert a3[1].params["rule"].firing_rule_index == (1, 0)
    assert a4[1].params["rule"].firing_rule_index == (1, 0)
    assert a3[1].params["size_increment"] == 1
    assert a4[1].params["size_increment"] == -1

    # Last run has no actions left
    result = agent.get_valid_actions()
    assert result == []


def test_get_valid_actions_two_tasks(two_tasks_solution: Solution):
    """
    This test is to ensure that the different action selection settings are working as expected.
    """

    timetable = two_tasks_solution.state.timetable
    new_timetable = (
        timetable.add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 3),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 5),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 7),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.SECOND_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 9),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.SECOND_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 11),
        )
        .add_firing_rule(
            RuleSelector(batching_rule_task_id=TimetableGenerator.SECOND_ACTIVITY, firing_rule_index=None),
            new_firing_rule=FiringRule.gte(RULE_TYPE.SIZE, 13),
        )
    )

    new_state = replace(two_tasks_solution.state, timetable=new_timetable)
    constraints = (
        ConstraintsGenerator(two_tasks_solution.state.bpmn_definition)
        .add_size_constraint(
            # For ModifyBatchSizeIfNoCostImprovement to propose a change,
            # we need to assume static costs
            cost_fn="1",
            max_size=50,
        )
        .constraints
    )

    store = Store.from_state_and_constraints(
        new_state,
        constraints,
    )

    store.settings.action_variation_selection = (
        ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    )
    store.settings.max_variants_per_action = 2
    store.settings.max_number_of_actions_per_iteration = 2
    store.settings.only_allow_low_last = False

    agent = TabuAgent(store)
    agent.catalog = [
        ModifySizeRuleByCostFnHighCosts,
        ModifySizeRuleByWTAction,
    ]
    agent.set_action_generators(store.solution)

    a1, a2 = agent.get_valid_actions()

    assert isinstance(a1[1], ModifySizeRuleByCostFnHighCosts)
    assert isinstance(a2[1], ModifySizeRuleByWTAction)

    assert a1[1].params["rule"].firing_rule_index == (0, 0)
    assert a2[1].params["rule"].firing_rule_index == (0, 0)
    assert a1[1].params["rule"].batching_rule_task_id == TimetableGenerator.SECOND_ACTIVITY
    assert a2[1].params["rule"].batching_rule_task_id == TimetableGenerator.SECOND_ACTIVITY

    a3, a4 = agent.get_valid_actions()

    assert isinstance(a3[1], ModifySizeRuleByCostFnHighCosts)
    assert isinstance(a4[1], ModifySizeRuleByWTAction)

    assert a3[1].params["rule"].firing_rule_index == (1, 0)
    assert a4[1].params["rule"].firing_rule_index == (1, 0)
    assert a3[1].params["rule"].batching_rule_task_id == TimetableGenerator.SECOND_ACTIVITY
    assert a4[1].params["rule"].batching_rule_task_id == TimetableGenerator.SECOND_ACTIVITY

    # Last run starts with second task
    a5, a6 = agent.get_valid_actions()
    assert isinstance(a5[1], ModifySizeRuleByCostFnHighCosts)
    assert isinstance(a6[1], ModifySizeRuleByWTAction)

    assert a5[1].params["rule"].firing_rule_index == (0, 0)
    assert a6[1].params["rule"].firing_rule_index == (0, 0)
    assert a5[1].params["rule"].batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert a6[1].params["rule"].batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY

    # Last run starts with first task
    _ = agent.get_valid_actions()

    # No more actions left
    result = agent.get_valid_actions()
    assert result == []
