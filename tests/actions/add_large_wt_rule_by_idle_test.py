from dataclasses import replace

import pytest

from o2.actions.batching_actions.add_large_wt_rule_by_idle_action import (
    AddLargeWTRuleByIdleAction,
)
from o2.models.constraints import LargeWtRuleConstraints
from o2.models.timetable import BATCH_TYPE, RULE_TYPE
from o2.store import Store
from tests.fixtures.test_helpers import first_valid
from tests.fixtures.timetable_generator import TimetableGenerator


@pytest.fixture
def large_wt_rule_store(one_task_store: Store) -> Store:
    state = one_task_store.base_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 2h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 2 * 60 * 60
        ),
        # Work from 9 to 17 (8h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9,
            17,
            include_end_hour=False,
            only_week_days=True,
        ),
        # One Case every 1h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            1 * 60 * 60,
            1 * 60 * 60,
        ),
        # Cases from 9:00 to 17:00
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9,
            17,
            include_end_hour=False,
            only_week_days=False,
        ),
        # Batch Size of 4 (Meaning 4 are needed to for a single batch)
        # All together will then take 1h
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 4, duration_distribution=1 / 4
            )
        ],
        total_cases=16,
    )

    store = Store.from_state_and_constraints(state, one_task_store.constraints)
    store.settings.override_action_variation_selection_for_inner_loop = True
    return store


def test_add_large_wt_rule_by_idle_basic(large_wt_rule_store: Store):
    input = large_wt_rule_store.solution

    _, action = first_valid(
        large_wt_rule_store, AddLargeWTRuleByIdleAction.rate_self(large_wt_rule_store, input)
    )
    assert action is not None

    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    # We expect 1h idle time, because:
    # the first ideling batch is the one starting to accumlate from 13:00
    # (as the first one is done after collecting 3x1h WT + 1h of processing time)
    # 13:00 - 14:00 is of course available, but would result in a 0h ready wt rule,
    # which are forbidden, therefore it propses the slot from 14:00 - 15:00,
    # which results in 1h idle time cutoff
    assert action.params["waiting_time"] == 3600


def test_add_large_wt_rule_by_idle_with_constraints(large_wt_rule_store: Store):
    # Add Constraints
    large_wt_rule_store.constraints = replace(
        large_wt_rule_store.constraints,
        batching_constraints=[
            LargeWtRuleConstraints(
                id="test",
                batch_type=BATCH_TYPE.PARALLEL,
                tasks=[TimetableGenerator.FIRST_ACTIVITY],
                rule_type=RULE_TYPE.LARGE_WT,
                min_wt=2 * 60 * 60 - 1,
                max_wt=24 * 60 * 60,
            )
        ],
    )

    input = large_wt_rule_store.solution

    # Check if action is still valid
    _, action = first_valid(
        large_wt_rule_store, AddLargeWTRuleByIdleAction.rate_self(large_wt_rule_store, input)
    )
    assert action is not None
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["waiting_time"] == 2 * 60 * 60
