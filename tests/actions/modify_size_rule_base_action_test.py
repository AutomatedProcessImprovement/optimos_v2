from typing import Literal

from o2.actions.batching_actions.modify_size_rule_by_wt_action import (
    ModifySizeRuleByWTAction,
    ModifySizeRuleByWTActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.rule_selector import RuleSelector
from o2.models.timetable import COMPARATOR, BatchingRule, FiringRule
from o2.store import Store
from tests.fixtures.test_helpers import (
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE + 1
    first_rule = store.base_timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifySizeRuleByWTAction(
        ModifySizeRuleByWTActionParamsType(
            rule=selector, size_increment=1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE - 1
    first_rule = store.base_timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifySizeRuleByWTAction(
        ModifySizeRuleByWTActionParamsType(
            rule=selector, size_increment=-1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_to_one(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 2)
        ],
    )
    new_size = 1
    first_rule = store.base_timetable.batch_processing[0]
    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifySizeRuleByWTAction(
        ModifySizeRuleByWTActionParamsType(
            rule=selector, size_increment=-1, duration_fn="1"
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def helper_rule_matches_size(rule: BatchingRule, size: int) -> Literal[True]:
    """Check if a given rule is of the expected size and has expected distribution."""
    assert len(rule.firing_rules) == 1
    assert len(rule.firing_rules[0]) == 1
    assert rule.firing_rules[0][0] == FiringRule(
        attribute=RULE_TYPE.SIZE, comparison=COMPARATOR.EQUAL, value=size
    )
    if size != 1:
        assert len(rule.size_distrib) == 2
        # Check for first distribution rule (that forbids execution without batching)
        assert rule.size_distrib[0].key == "1"
        assert rule.size_distrib[0].value == 0
        # Check for actual distribution rule
        assert rule.size_distrib[1].key == str(size)
    else:
        # Check for actual distribution rule
        assert len(rule.size_distrib) == 1
        assert rule.size_distrib[0].key == str(size)
        assert rule.size_distrib[0].value == 1

    return True
