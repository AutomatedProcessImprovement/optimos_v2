from optimos_v2.src.actions.base_action import BaseAction, BaseActionParamsType
from optimos_v2.src.types.state import State


class RemoveRuleActionParamsType(BaseActionParamsType):
    rule_hash: str


class RemoveRuleAction(BaseAction):
    params: RemoveRuleActionParamsType

    # Returns a copy of the timetable with the rule removed
    # (TimetableType is a frozen dataclass)
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        rule_hash = self.params["rule_hash"]

        rule_index = next(
            (
                i
                for i, rule in enumerate(timetable.batch_processing)
                if rule.id() == rule_hash
            ),
            None,
        )
        if rule_index is None:
            print(f"Rule with hash {rule_hash} not found")
            return state
        if enable_prints:
            print(f"\t\t>> Removing rule {rule_hash}")
        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:rule_index]
            + timetable.batch_processing[rule_index + 1 :],
        )
