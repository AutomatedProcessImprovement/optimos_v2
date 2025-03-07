from dataclasses import replace

from o2.actions.batching_actions.modify_size_rule_by_cost_fn import (
    ModifyBatchSizeIfNoCostImprovement,
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnLowProcessingTime,
)
from o2.agents.tabu_agent import TabuAgent
from o2.models.rule_selector import RuleSelector
from o2.models.settings import ActionVariationSelection
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE, FiringRule
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_get_valid_actions(one_task_solution: Solution):
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
