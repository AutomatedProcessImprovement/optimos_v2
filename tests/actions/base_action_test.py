from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.batching_actions.add_date_time_rule_by_availability_action import (
    AddDateTimeRuleByAvailabilityAction,
)
from o2.actions.batching_actions.add_date_time_rule_by_enablement_action import (
    AddDateTimeRuleByEnablementAction,
)
from o2.actions.batching_actions.modify_size_rule_by_allocation_action import (
    ModifySizeRuleByAllocationActionParamsType,
    ModifySizeRuleByLowAllocationAction,
)
from o2.actions.batching_actions.modify_size_rule_by_cost_action import (
    ModifySizeRuleByCostAction,
    ModifySizeRuleByCostActionParamsType,
)
from o2.agents.tabu_agent import TabuAgent
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING
from o2.models.timetable.time_period import TimePeriod
from o2.store import Store
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_hashing():
    rule1 = ModifySizeRuleByCostAction(
        params=ModifySizeRuleByCostActionParamsType(
            rule=RuleSelector(batching_rule_task_id="task_1", firing_rule_index=(0, 0)),
            size_increment=1,
            duration_fn="1",
        )
    )
    rule2 = ModifySizeRuleByLowAllocationAction(
        params=ModifySizeRuleByAllocationActionParamsType(
            rule=RuleSelector(batching_rule_task_id="task_1", firing_rule_index=(0, 0)),
            size_increment=1,
            duration_fn="1",
        )
    )
    rule3 = ModifySizeRuleByLowAllocationAction(
        params=ModifySizeRuleByAllocationActionParamsType(
            rule=RuleSelector(batching_rule_task_id="task_1", firing_rule_index=(0, 0)),
            size_increment=-1,
            duration_fn="1",
        )
    )
    rule4 = ModifySizeRuleByLowAllocationAction(
        params=ModifySizeRuleByAllocationActionParamsType(
            rule=RuleSelector(batching_rule_task_id="task_1", firing_rule_index=(0, 1)),
            size_increment=1,
            duration_fn="1",
        )
    )
    assert rule1.id == rule2.id
    assert rule1.id != rule3.id
    assert rule1.id != rule4.id


def test_get_valid_actions(one_task_store: Store):
    def rule1_generator():
        yield (
            RATING.HIGH,
            AddDateTimeRuleByAvailabilityAction(
                params=AddDateTimeRuleBaseActionParamsType(
                    task_id=TimetableGenerator.FIRST_ACTIVITY,
                    time_period=TimePeriod.from_start_end(10, 12),
                    duration_fn="1",
                )
            ),
        )

    def rule2_generator():
        yield (
            RATING.HIGH,
            AddDateTimeRuleByEnablementAction(
                params=AddDateTimeRuleBaseActionParamsType(
                    task_id=TimetableGenerator.FIRST_ACTIVITY,
                    time_period=TimePeriod.from_start_end(10, 12),
                    duration_fn="1",
                )
            ),
        )

    agent = TabuAgent(one_task_store)
    agent.action_generators = [rule1_generator(), rule2_generator()]
    actions = agent.get_valid_actions()
    assert actions is not None
    assert len(actions) == 1
