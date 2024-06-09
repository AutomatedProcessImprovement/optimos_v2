from dataclasses import dataclass
from enum import Enum

from o2.types.evaluation import Evaluation
from o2.types.rule_selector import RuleSelector


class RATING(float, Enum):
    NOT_APPLICABLE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 99


@dataclass
class SelfRatingInput:
    # A Evaluation object,
    # containing the results of the simulation without
    # the key rule active
    rule_evaluations: dict[RuleSelector, Evaluation]
    most_impactful_rule: RuleSelector

    @property
    def most_impactful_rule_evaluation(self):
        return self.rule_evaluations[self.most_impactful_rule]

    @staticmethod
    def from_rule_evaluations(evaluations: dict[RuleSelector, Evaluation]):
        if len(evaluations) == 0:
            return None
        # Find the rule that has the most impact,
        # aka. the one that, after being removed, has reduced the waiting time the most
        # and therefore has the most potential to improve the current fastest evaluation
        # TODO: Make this abs, to look for positively impactful rules
        most_impactful_rule_selector = min(
            evaluations,
            key=lambda rule_selector: evaluations[rule_selector].total_waiting_time,
        )

        return SelfRatingInput(
            rule_evaluations=evaluations,
            most_impactful_rule=most_impactful_rule_selector,
        )
