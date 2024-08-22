import concurrent.futures
import os
import traceback

from o2.actions.action_selector import ActionSelector
from o2.actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.pareto_front import FRONT_STATUS
from o2.store import ActionTry, Store
from o2.util.indented_printer import print_l0, print_l1, print_l2, print_l3

MAX_PARALLEL = os.cpu_count() or 1


class HillClimber:
    def __init__(self, store: Store, max_iter=None, max_parallel=MAX_PARALLEL):
        self.store = store
        self.max_iter = max_iter or store.settings.max_iterations
        self.max_non_improving_iter = store.settings.max_iterations
        self.max_parallel = max_parallel
        self.executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_parallel
        )

    def solve(self):
        print_l0("Running Base Evaluation...")
        self.store.evaluate()
        print_l1(
            f"Initial evaluation: {self.store.current_pareto_front.evaluations[-1]}"
        )
        for it in range(self.max_iter):
            try:
                if self.max_non_improving_iter <= 0:
                    print("Maxium non improving iterations reached")
                    break
                print_l0(f"Iteration {it}")

                actions_to_perform = ActionSelector.select_actions(
                    self.store, number_of_actions_to_select=self.max_parallel
                )
                if actions_to_perform is None or len(actions_to_perform) == 0:
                    print_l1("No actions left")
                    break
                print_l1("Running actions...")

                action_tries = self._execute_actions_parallel(
                    self.store, actions_to_perform
                )
                chosen_tries, not_chosen_tries = self.store.proccess_many_action_tries(
                    action_tries
                )

                if len(chosen_tries) == 0:
                    print_l1("No action improved the evaluation")
                    self.max_non_improving_iter -= len(actions_to_perform)
                    for _, _, _, action in not_chosen_tries:
                        print_l2(str(action))
                else:
                    if len(not_chosen_tries) > 0:
                        print_l1("Actions NOT chosen:")
                    for _, _, _, action in not_chosen_tries:
                        print_l2(str(action))
                        self.max_non_improving_iter -= 1
                    print_l1("Actions chosen:")
                    for status, evaluation, _, action in chosen_tries:
                        print_l2(str(action))
                        if status == FRONT_STATUS.IN_FRONT:
                            print_l3("Result Pareto front CONTAINS new evaluation.")
                            print_l3(f"Evaluation: {evaluation}")
                        elif status == FRONT_STATUS.IS_DOMINATED:
                            print_l3("Pareto front IS DOMINATED by new evaluation.")
                            print_l3(f"New best Evaluation: {evaluation}")
                            self.max_non_improving_iter = (
                                self.store.settings.max_non_improving_actions
                            )

            except Exception as e:
                print_l1(f"Error in iteration: {e}")
                print_l1(traceback.format_exc())
                continue
        self.executor.shutdown()
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

    def _execute_actions_parallel(
        self, store: Store, actions_to_perform: list[BaseAction]
    ) -> list[ActionTry]:
        """Execute the given actions in parallel and return the results.

        The results are sorted, so that the most impactful actions are first,
        thereby allowing the store to process them in that order.
        The results have not modified the state of the store.

        """
        action_tries = []

        futures: list[concurrent.futures.Future[ActionTry]] = []
        for action in actions_to_perform:
            futures.append(
                self.executor.submit(
                    store.tryAction,
                    action,
                )
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                action_try = future.result()
                action_tries.append(action_try)
            except Exception as e:
                print_l1(f"Error in future: {e}")
                continue
        # Sort tries with dominating ones first
        action_tries.sort(
            key=lambda x: -1
            if x[0] == FRONT_STATUS.IS_DOMINATED
            else 1
            if x[0] == FRONT_STATUS.DOMINATES
            else 0
        )
        return action_tries
