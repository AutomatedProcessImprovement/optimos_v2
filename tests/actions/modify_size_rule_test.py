from dataclasses import replace

import pandas as pd
from o2.store import Store
from o2.actions.action_selector import ActionSelector
from optimos_v2.o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
    ModifySizeRuleActionParamsType,
)
from optimos_v2.o2.types.constraints import RULE_TYPE
from optimos_v2.o2.types.timetable import COMPARATOR, BatchingRule, FiringRule
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE + 1
    first_rule = store.state.timetable.batch_processing[0]
    action = ModifySizeRuleAction(
        ModifySizeRuleActionParamsType(
            rule_hash=first_rule.id(), size_increment=1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert check_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE - 1
    first_rule = store.state.timetable.batch_processing[0]
    action = ModifySizeRuleAction(
        ModifySizeRuleActionParamsType(
            rule_hash=first_rule.id(), size_increment=-1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert check_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def check_rule_matches_size(rule: BatchingRule, size: int):
    assert len(rule.firing_rules) == 1
    assert len(rule.firing_rules[0]) == 1
    assert rule.firing_rules[0][0] == FiringRule(
        attribute=RULE_TYPE.SIZE, comparison=COMPARATOR.EQUAL, value=size
    )
    assert len(rule.size_distrib) == 2
    # Check for first distribution rule (that forbids execution without batching)
    assert rule.size_distrib[0].key == "1"
    assert rule.size_distrib[0].value == 0
    # Check for actual distribution rule
    assert rule.size_distrib[1].key == str(size)
    return True
