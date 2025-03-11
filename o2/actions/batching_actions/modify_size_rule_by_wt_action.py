from typing_extensions import override

from o2.actions.base_actions.add_size_rule_base_action import (
    AddSizeRuleAction,
    AddSizeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store
from o2.util.helper import select_variants


class ModifySizeRuleByWTActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByWTAction."""

    pass


class ModifySizeRuleByWTAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on waiting time.

    1. Gets the tasks with the most waiting time
    2. Looks if theres a size rule for that task
    3. If there is, it decrements the size by 1
    """

    params: ModifySizeRuleByWTActionParamsType

    @override
    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByWTAction | AddSizeRuleAction"]:
        timetable = store.current_timetable
        avg_batching_waiting_time_per_task = store.current_evaluation.avg_batching_waiting_time_per_task
        sorted_tasks = sorted(
            avg_batching_waiting_time_per_task.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for task_id, waiting_time in sorted_tasks:
            if (waiting_time) < 1:
                continue
            duration_fn = store.constraints.get_duration_fn_for_task(task_id)

            selectors = timetable.get_firing_rule_selectors_for_task(task_id, rule_type=RULE_TYPE.SIZE)
            if not selectors:
                yield (
                    RATING.LOW,
                    AddSizeRuleAction(
                        AddSizeRuleBaseActionParamsType(
                            task_id=task_id,
                            size=2,
                            duration_fn=duration_fn,
                        )
                    ),
                )
            for selector in select_variants(store, selectors):
                yield (
                    RATING.LOW,
                    ModifySizeRuleByWTAction(
                        ModifySizeRuleByWTActionParamsType(
                            rule=selector,
                            size_increment=-1,
                            duration_fn=duration_fn,
                        )
                    ),
                )
