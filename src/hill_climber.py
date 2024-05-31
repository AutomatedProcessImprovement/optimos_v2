from src.pareto_front import FRONT_STATUS
from src.action_selector import ActionSelector
from src.store import Store
from src.types.state import State


class HillClimber:
    def __init__(self, store: Store, max_iter=1000):
        self.store = store
        self.max_iter = max_iter

    def solve(self):
        print("running base evaluation...")
        self.store.evaluate()
        print(f"\t> Initial evaluation: {self.store.current_pareto_front}")
        for it in range(self.max_iter):
            print(f"Iteration {it}")

            action_to_perform = ActionSelector.select_action(self.store)
            if action_to_perform is None:
                print("\t> No actions left")
                break
            self.store.apply_action(action_to_perform)
            print(f"\t> Performing action {str(action_to_perform)}")
            (evaluation, status) = self.store.evaluate()
            if status == FRONT_STATUS.IS_DOMINATED:
                print(
                    f"\t> New Evaluation DOMINATED by current pareto front. Undoing action {action_to_perform}"
                )
                self.store.undo_action()
            elif status == FRONT_STATUS.DOMINATES:
                # This is the best evaluation so far,
                # so we reset the tabu list
                print(
                    f"\t> New Evaluation DOMINATES old pareto front. New best Evaluation: {evaluation}"
                )
                self.store.reset_tabu_list()
            elif status == FRONT_STATUS.IN_FRONT:
                print(
                    f"\t> New Evaluation IN current pareto front. Evaluation: {evaluation}"
                )

        self.print_result()

    def print_result(self):
        print(f"Best evaluation: \t{self.store.current_pareto_front}")
        print(f"Base evaluation: \t{self.store.base_evaluation}")
        print(
            f"Modifications: {', '.join(list(map(str, self.store.previous_actions)))}"
        )
