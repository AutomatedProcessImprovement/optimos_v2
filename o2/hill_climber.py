from o2.actions.action_selector import ActionSelector
from o2.pareto_front import FRONT_STATUS
from o2.store import Store
from o2.util.indented_printer import print_l0, print_l1, print_l2


class HillClimber:
    def __init__(self, store: Store, max_iter=1000):
        self.store = store
        self.max_iter = max_iter
        self.max_non_improving_iter = 25

    def solve(self):
        print_l0("Base Evaluation")
        self.store.evaluate()
        print_l0(
            f"Initial evaluation: {self.store.current_pareto_front.evaluations[-1]}"
        )
        for it in range(self.max_iter):
            try:
                if self.max_non_improving_iter == 0:
                    print("Max non improving iterations reached")
                    break
                print_l0(f"Iteration {it}")

                action_to_perform = ActionSelector.select_action(self.store)
                if action_to_perform is None:
                    print_l1("No actions left")
                    break
                print_l1("Performing action:")
                print_l2(str(action_to_perform))
                self.store.apply_action(action_to_perform)
                (evaluation, status) = self.store.evaluate()
                if status == FRONT_STATUS.DOMINATES:
                    print_l1(
                        f"Pareto front DOMINATED new evaluation. Undoing action {action_to_perform}"
                    )
                    print_l2(f"Evaluation: {evaluation}")
                    self.store.undo_action()
                    self.max_non_improving_iter -= 1

                elif status == FRONT_STATUS.IS_DOMINATED:
                    # This is the best evaluation so far,
                    # so we reset the tabu list
                    print_l1("Pareto front IS DOMINATED by new evaluation.")
                    print_l2(f"New best Evaluation: {evaluation}")
                    self.store.reset_tabu_list()
                    self.max_non_improving_iter = 25
                elif status == FRONT_STATUS.IN_FRONT:
                    print_l1("Pareto front CONTAINS new evaluation.")
                    print_l2(f"Evaluation: {evaluation}")
            except Exception as e:
                print_l1(f"Error in iteration, skipping & undoing action: {e}")
                self.store.undo_action()
                continue

        self._print_result()

    def _print_result(self):
        print_l0("Final result:")
        print_l1(
            f"Best evaluation: \t{self.store.current_pareto_front.evaluations[-1]}"
        )
        print_l1(f"Base evaluation: \t{self.store.base_evaluation}")
        print_l1("Modifications:")
        for action in self.store.previous_actions:
            print_l2(str(action))
