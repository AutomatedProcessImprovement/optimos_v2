from o2.actions.action_selector import ActionSelector
from o2.pareto_front import FRONT_STATUS

from o2.store import Store
from o2.types.state import State


class HillClimber:
    def __init__(self, store: Store, max_iter=1000):
        self.store = store
        self.max_iter = max_iter
        self.max_non_improving_iter = 25

    def solve(self):
        print("Base Evaluation")
        self.store.evaluate()
        print(
            f"\t> Initial evaluation: {self.store.current_pareto_front.evaluations[-1]}"
        )
        for it in range(self.max_iter):
            try:
                if self.max_non_improving_iter == 0:
                    print("Max non improving iterations reached")
                    break
                print(f"Iteration {it}")

                action_to_perform = ActionSelector.select_action(self.store)
                if action_to_perform is None:
                    print("\t> No actions left")
                    break
                self.store.apply_action(action_to_perform)
                print(f"\t> Performing action {str(action_to_perform)}")
                (evaluation, status) = self.store.evaluate()
                if status == FRONT_STATUS.DOMINATES:
                    print(
                        f"\t> Pareto front DOMINATED new evaluation. Undoing action {action_to_perform}"
                    )
                    self.store.undo_action()
                    self.max_non_improving_iter -= 1

                elif status == FRONT_STATUS.IS_DOMINATED:
                    # This is the best evaluation so far,
                    # so we reset the tabu list
                    print(
                        f"\t> Pareto front IS DOMINATED by new evaluation. New best Evaluation: {evaluation}"
                    )
                    self.store.reset_tabu_list()
                    self.max_non_improving_iter = 25
                elif status == FRONT_STATUS.IN_FRONT:
                    print(
                        f"\t> Pareto front CONTAINS new evaluation. Evaluation: {evaluation}"
                    )
            except Exception as e:
                print(f"\t> Error in iteration, skipping & undoing action: {e}")
                self.store.undo_action()
                continue

        self.print_result()

    def print_result(self):
        print(f"Best evaluation: \t{self.store.current_pareto_front.evaluations[-1]}")
        print(f"Base evaluation: \t{self.store.base_evaluation}")
        print(
            f"Modifications: {', '.join(list(map(str, self.store.previous_actions)))}"
        )
