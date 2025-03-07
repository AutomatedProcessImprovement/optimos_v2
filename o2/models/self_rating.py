from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector

if TYPE_CHECKING:
    from o2.models.solution import Solution
    from o2.store import Store


class RATING(float, Enum):
    NOT_APPLICABLE = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    EXTREME = 99


@dataclass(frozen=True)
class SelfRatingInput:
    """A class that holds the input for the self-rating of a rule."""

    parent_solution: "Solution"
    """The previous solution, before the rule was applied."""
    rule_solutions: dict[RuleSelector, "Solution"]
    most_impactful_rule: Optional[RuleSelector]

    @property
    def most_impactful_rule_evaluation(self) -> Optional[Evaluation]:
        """Return the evaluation of the most impactful rule."""
        if self.most_impactful_rule is None:
            return None
        return self.rule_solutions[self.most_impactful_rule].evaluation

    @property
    def most_wt_increase(self) -> Optional[RuleSelector]:
        """Return the rule that has the most negative impact on the waiting time.

        Meaning the rule, that when removed reduced the waiting time the most.
        """
        increasing_rules = {
            rule_selector: solution
            for rule_selector, solution in self.rule_solutions.items()
            if solution.evaluation.total_waiting_time < self.parent_solution.evaluation.total_waiting_time
        }
        if len(increasing_rules) == 0:
            return None
        return max(
            increasing_rules,
            key=lambda rule_selector: self.parent_solution.evaluation.total_waiting_time
            - self.rule_solutions[rule_selector].evaluation.total_waiting_time,
        )

    @property
    def most_wt_increase_evaluation(self) -> Evaluation:
        """Return the evaluation of the `most_wt_increase` rule."""
        most_wt_increase = self.most_wt_increase
        if most_wt_increase is None:
            return Evaluation.empty()
        return self.rule_solutions[most_wt_increase].evaluation

    @property
    def most_wt_reduction(self) -> Optional[RuleSelector]:
        """Return the rule that has the most positive impact on the waiting time.

        Meaning the rule, that when removed increased the waiting time the most.
        """
        reducing_rules = {
            rule_selector: solution
            for rule_selector, solution in self.rule_solutions.items()
            if solution.evaluation.total_waiting_time > self.parent_solution.evaluation.total_waiting_time
        }
        if len(reducing_rules) == 0:
            return None
        return min(
            reducing_rules,
            key=lambda rule_selector: self.parent_solution.evaluation.total_waiting_time
            - self.rule_solutions[rule_selector].evaluation.total_waiting_time,
        )

    @property
    def most_wt_reduction_evaluation(self) -> Evaluation:
        """Return the evaluation of the `most_wt_reduction` rule."""
        most_wt_reduction = self.most_wt_reduction
        if most_wt_reduction is None:
            return Evaluation.empty()
        return self.rule_solutions[most_wt_reduction].evaluation

    @property
    def parent_evaluation(self) -> Evaluation:
        """Return the evaluation of the parent solution."""
        return self.parent_solution.evaluation

    @staticmethod
    def from_rule_solutions(
        store: "Store", solutions: dict[RuleSelector, "Solution"]
    ) -> Union["SelfRatingInput", None]:
        """Create a SelfRatingInput object from a list of evaluations."""
        if len(solutions) == 0:
            return None
        base = store.solution

        # Find the rule that has the most impact,
        # aka. the one that, after being removed, has reduced the waiting time the most
        # and therefore has the most potential to improve the current fastest evaluation
        most_impactful_rule_selector = max(
            solutions,
            key=lambda rule_selector: abs(
                base.evaluation.total_waiting_time - solutions[rule_selector].evaluation.total_waiting_time
            ),
        )

        return SelfRatingInput(
            parent_solution=base,
            rule_solutions=solutions,
            most_impactful_rule=most_impactful_rule_selector,
        )

    @staticmethod
    def from_base_solution(base_solution: "Solution") -> "SelfRatingInput":
        """Create a SelfRatingInput object from a base evaluation.

        Please only use this if you are know what you are doing, or in tests!
        """
        return SelfRatingInput(
            parent_solution=base_solution,
            rule_solutions={},
            most_impactful_rule=None,
        )

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return (
            "SelfRatingInput(\n"
            + "\n".join(
                f"{rule_selector}:\t{str(evaluation)}"
                for (rule_selector, evaluation) in self.rule_solutions.items()
            )
            + "\nBase Evaluation:\t"
            + str(self.parent_solution)
            + f"\nMost Impact:\t{self.most_impactful_rule})"
        )
