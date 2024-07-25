from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from o2.store import Store

from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector


class RATING(float, Enum):
    NOT_APPLICABLE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 99


@dataclass(frozen=True)
class SelfRatingInput:
    # A Evaluation object,
    # containing the results of the simulation without
    # the key rule active
    base_evaluation: Evaluation
    rule_evaluations: dict[RuleSelector, Evaluation]
    most_impactful_rule: RuleSelector

    @property
    def most_impactful_rule_evaluation(self) -> Evaluation:
        """Return the evaluation of the most impactful rule."""
        return self.rule_evaluations[self.most_impactful_rule]

    @property
    def most_wt_increase(self) -> Optional[RuleSelector]:
        """Return the rule that has the most negative impact on the waiting time.

        Meaning the rule, that when removed reduced the waiting time the most.
        """
        increasing_rules = {
            rule_selector: evaluation
            for rule_selector, evaluation in self.rule_evaluations.items()
            if evaluation.total_waiting_time < self.base_evaluation.total_waiting_time
        }
        if len(increasing_rules) == 0:
            return None
        return max(
            increasing_rules,
            key=lambda rule_selector: self.base_evaluation.total_waiting_time
            - self.rule_evaluations[rule_selector].total_waiting_time,
        )

    @property
    def most_wt_increase_evaluation(self) -> Evaluation:
        """Return the evaluation of the `most_wt_increase` rule."""
        most_wt_increase = self.most_wt_increase
        if most_wt_increase is None:
            return Evaluation.empty()
        return self.rule_evaluations[most_wt_increase]

    @property
    def most_wt_reduction(self) -> Optional[RuleSelector]:
        """Return the rule that has the most positive impact on the waiting time.

        Meaning the rule, that when removed increased the waiting time the most.
        """
        reducing_rules = {
            rule_selector: evaluation
            for rule_selector, evaluation in self.rule_evaluations.items()
            if evaluation.total_waiting_time > self.base_evaluation.total_waiting_time
        }
        if len(reducing_rules) == 0:
            return None
        return min(
            reducing_rules,
            key=lambda rule_selector: self.base_evaluation.total_waiting_time
            - self.rule_evaluations[rule_selector].total_waiting_time,
        )

    @property
    def most_wt_reduction_evaluation(self) -> Evaluation:
        """Return the evaluation of the `most_wt_reduction` rule."""
        most_wt_reduction = self.most_wt_reduction
        if most_wt_reduction is None:
            return Evaluation.empty()
        return self.rule_evaluations[most_wt_reduction]

    @staticmethod
    def from_rule_evaluations(
        store: Store, evaluations: dict[RuleSelector, Evaluation]
    ) -> Union["SelfRatingInput", None]:
        """Create a SelfRatingInput object from a list of evaluations."""
        if len(evaluations) == 0:
            return None
        base = store.current_fastest_evaluation

        # Find the rule that has the most impact,
        # aka. the one that, after being removed, has reduced the waiting time the most
        # and therefore has the most potential to improve the current fastest evaluation
        most_impactful_rule_selector = max(
            evaluations,
            key=lambda rule_selector: abs(
                base.total_waiting_time - evaluations[rule_selector].total_waiting_time
            ),
        )

        return SelfRatingInput(
            base_evaluation=base,
            rule_evaluations=evaluations,
            most_impactful_rule=most_impactful_rule_selector,
        )

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return (
            "SelfRatingInput(\n"
            + "\n".join(
                f"{rule_selector}:\t{str(evaluation)}"
                for (rule_selector, evaluation) in self.rule_evaluations.items()
            )
            + "\nBase Evaluation:\t"
            + str(self.base_evaluation)
            + f"\nMost Impact:\t{self.most_impactful_rule})"
        )
