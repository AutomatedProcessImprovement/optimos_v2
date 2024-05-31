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
        print(f"\t> Initial evaluation: {self.store.current_evaluation}")
        best_evaluation = self.store.current_evaluation
        for it in range(self.max_iter):
            print(f"Iteration {it}")

            action_to_perform = ActionSelector.select_action(self.store)
            if action_to_perform is None:
                print("\t>No actions left")
                break
            self.store.apply_action(action_to_perform)
            print(f"\t> Performing action {str(action_to_perform)}")
            new_evaluation = self.store.evaluate()
            if new_evaluation <= best_evaluation:
                print(f"\t> Undoing action {action_to_perform}")
                self.store.undo_action()
            else:
                # This is the best evaluation so far,
                # so we reset the tabu list
                print(f"\t> Keeping Action, new best Evaluation: {new_evaluation}")
                best_evaluation = new_evaluation
                self.store.reset_tabu_list()
        self.print_result()

    def print_result(self):
        print(f"Best evaluation: \t{self.store.current_evaluation}")
        print(f"Base evaluation: \t{self.store.previous_evaluations[0]}")
        print(
            f"Modifications: {', '.join(list(map(str, self.store.previous_actions)))}"
        )
