import concurrent.futures
import os
import time
import traceback
from typing import Generator

from o2.actions.action_selector import ActionSelector
from o2.actions.base_action import BaseAction
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l0, print_l1, print_l2, print_l3


class HillClimber:
    """The Hill Climber class is the main class that runs the optimization process."""

    def __init__(self, store: Store):
        self.store = store
        self.max_iter = store.settings.max_iterations
        self.max_non_improving_iter = store.settings.max_non_improving_actions
        self.max_parallel = store.settings.max_threads
        if not store.settings.disable_parallel_evaluation:
            self.executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.store.settings.max_threads
            )

    def solve(self) -> None:
        """Run the hill climber and print the result."""
        print_l1(f"Initial evaluation: {self.store.base_solution.evaluation}")
        generator = self.get_iteration_generator()
        for _ in generator:
            # Just iterate through the generator to run it
            pass

        if not self.store.settings.disable_parallel_evaluation:
            self.executor.shutdown()
        self._print_result()

    def get_iteration_generator(self) -> Generator[Solution, None, None]:
        """Run the hill climber and yield optimal Solution.

        NOTE: You usually want to use the `solve` method instead of this
        method, but if you want to process the Solution as they come,
        you can use this method.
        """
        for it in range(self.max_iter):
            try:
                if self.max_non_improving_iter <= 0:
                    print("Maximum non improving iterations reached")
                    break
                print_l0(f"Iteration {it}")

                actions_to_perform = ActionSelector.select_actions(self.store)
                if actions_to_perform is None or len(actions_to_perform) == 0:
                    print_l1("Iteration finished, no actions to perform.")
                    break
                print_l1(f"Running {len(actions_to_perform)} actions...")
                start_time = time.time()

                solutions = self._execute_actions_parallel(
                    self.store, actions_to_perform
                )
                print_l2(f"Simulation took {time.time() - start_time:.2f}s")

                chosen_tries, not_chosen_tries = self.store.process_many_solutions(
                    solutions
                )

                if len(chosen_tries) == 0:
                    print_l1("No action improved the evaluation")
                    self.max_non_improving_iter -= len(actions_to_perform)
                    for _, solution in not_chosen_tries:
                        print_l2(str(solution.last_action))
                else:
                    if len(not_chosen_tries) > 0:
                        print_l1("Actions NOT chosen:")
                    for _, solution in not_chosen_tries:
                        print_l2(str(solution.last_action))
                        self.max_non_improving_iter -= 1
                    print_l1("Actions chosen:")
                    for status, solution in chosen_tries:
                        print_l2(str(solution.last_action))
                        if status == FRONT_STATUS.IN_FRONT:
                            print_l3("Result Pareto front CONTAINS new evaluation.")
                            print_l3(f"Evaluation: {solution.evaluation}")
                            yield solution
                        elif status == FRONT_STATUS.IS_DOMINATED:
                            print_l3("Pareto front IS DOMINATED by new evaluation.")
                            print_l3(f"New best Evaluation: {solution.evaluation}")
                            self.max_non_improving_iter = (
                                self.store.settings.max_non_improving_actions
                            )
                            yield solution

            except Exception as e:
                print_l1(f"Error in iteration: {e}")
                print_l1(traceback.format_exc())
                continue

    def _print_result(self):
        print_l0("Final result:")
        print_l1(f"Best evaluation: \t{self.store.current_evaluation}")
        print_l1(f"Base evaluation: \t{self.store.base_evaluation}")
        print_l1("Modifications:")
        for action in self.store.base_solution.actions:
            print_l2(str(action))

    def _execute_actions_parallel(
        self, store: Store, actions_to_perform: list[BaseAction]
    ) -> list[Solution]:
        """Execute the given actions in parallel and return the results.

        The results are sorted, so that the most impactful actions are first,
        thereby allowing the store to process them in that order.
        The results have not modified the state of the store.

        """
        solution_tries: list[SolutionTry] = []

        if not store.settings.disable_parallel_evaluation:
            futures: list[concurrent.futures.Future[Solution]] = []
            for action in actions_to_perform:
                futures.append(
                    self.executor.submit(Solution.from_parent, store.solution, action)
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    new_solution = future.result()
                    solution_tries.append(self.store.try_solution(new_solution))
                except Exception as e:
                    print_l1(f"Error evaluating actions : {e}")
        else:
            for action in actions_to_perform:
                solution_try = store.try_solution(
                    Solution.from_parent(store.solution, action)
                )
                solution_tries.append(solution_try)

        # Sort tries with dominating ones first
        solution_tries.sort(
            key=lambda x: -1
            if x[0] == FRONT_STATUS.IS_DOMINATED
            else 1
            if x[0] == FRONT_STATUS.DOMINATES
            else 0
        )
        return list(map(lambda x: x[1], solution_tries))
