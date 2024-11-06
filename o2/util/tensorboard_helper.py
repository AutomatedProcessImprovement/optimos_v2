from datetime import datetime
import time
import tensorflow as tf

from o2.agents.agent import Agent
from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.models.solution import Solution
from o2.store import Store
from o2.util.indented_printer import print_l2, print_l3

log_dir = "./logs/optimos_v2_tensorboard"


# Metrics:
# - Current best solution cost + time
# - Current Temperature
# - No of solutions tried
# - No of solutions left in the queue
# - No of solutions already tried


class TensorBoardHelper:
    instance: "TensorBoardHelper"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.store: "Store" = self.agent.store
        self.name = f"{self.store.settings.agent.name}_{datetime.now().isoformat()}"
        self.writer = tf.summary.create_file_writer(
            f"{log_dir}/{self.name}",
            name=self.name,
        )
        self.step = 0
        TensorBoardHelper.instance = self

    def tensor_board_iteration_callback(self, solution: Solution) -> None:
        """Log the current solution to TensorBoard."""  # noqa: D401
        start_time = time.time()
        with self.writer.as_default():
            self.step += 1
            if isinstance(self.agent, SimulatedAnnealingAgent):
                tf.summary.scalar(
                    "sa/temperature", self.agent.temperature, step=self.step
                )
                solutions_left_for_temperature = len(
                    self.store.solution_tree.get_solutions_near_to_pareto_front(
                        self.store.current_pareto_front,
                        max_distance=self.agent.temperature,
                    )
                )
                tf.summary.scalar(
                    "sa/solutions_left_for_temperature",
                    solutions_left_for_temperature,
                    step=self.step,
                )

            tf.summary.scalar(
                "current_base/total_cost_for_available_time",
                self.store.current_evaluation.total_cost_for_available_time,
                step=self.step,
            )

            tf.summary.scalar(
                "current_base/total_cycle_time",
                self.store.current_evaluation.total_cycle_time,
                step=self.step,
            )

            tf.summary.scalar(
                "current_base/total_waiting_time",
                self.store.current_evaluation.total_waiting_time,
                step=self.step,
            )

            tf.summary.scalar(
                "front/avg_total_cost_for_available_time",
                self.store.current_pareto_front.avg_total_cost_for_available_time,
                step=self.step,
            )
            tf.summary.scalar(
                "front/avg_total_cycle_time",
                self.store.current_pareto_front.avg_total_cycle_time,
                step=self.step,
            )

            discarded_solutions = self.store.solution_tree.discarded_solutions
            tf.summary.scalar(
                "global/solutions_tried",
                discarded_solutions,
                step=self.step,
            )
            tf.summary.scalar(
                "global/solutions_left",
                self.store.solution_tree.total_solutions - discarded_solutions,
                step=self.step,
            )

        print_l3(f"Logged to TensorBoard in {time.time() - start_time:.2f}s")
