import os
import shutil
import time
from datetime import datetime

import tensorflow as tf

from o2.agents.agent import Agent
from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store

TENSORBOARD_LOG_DIR = "./logs/optimos_v2_tensorboard"
TENSORBOARD_LOG_DIR_ARCHIVE = f"{TENSORBOARD_LOG_DIR}_archive"

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
            f"{TENSORBOARD_LOG_DIR}/{self.name}",
            name=self.name,
        )
        self.step = 0
        TensorBoardHelper.instance = self

    def tensor_board_iteration_callback(self, solution: Solution) -> None:
        """Log the current solution to TensorBoard."""  # noqa: D401
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
                "current_base/total_cost",
                self.store.current_evaluation.total_cost,
                step=self.step,
            )

            tf.summary.scalar(
                "current_base/total_duration",
                self.store.current_evaluation.total_duration,
                step=self.step,
            )

            tf.summary.scalar(
                "current_base/total_waiting_time",
                self.store.current_evaluation.total_waiting_time,
                step=self.step,
            )

            tf.summary.scalar(
                "front/avg_" + Settings.get_pareto_x_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.avg_x,
                step=self.step,
            )
            tf.summary.scalar(
                "front/avg_" + Settings.get_pareto_y_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.avg_y,
                step=self.step,
            )

            tf.summary.scalar(
                "front/max_" + Settings.get_pareto_x_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.max_x,
                step=self.step,
            )
            tf.summary.scalar(
                "front/max_ " + Settings.get_pareto_y_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.max_y,
                step=self.step,
            )

            tf.summary.scalar(
                "front/min_" + Settings.get_pareto_x_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.min_x,
                step=self.step,
            )
            tf.summary.scalar(
                "front/min_ " + Settings.get_pareto_y_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.min_y,
                step=self.step,
            )

            if Settings.COST_TYPE != CostType.TOTAL_COST:
                tf.summary.scalar(
                    "front/avg_total_cost",
                    self.store.current_pareto_front.avg_total_cost,
                    step=self.step,
                )
            tf.summary.scalar(
                "front/size",
                self.store.current_pareto_front.size,
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

        # print_l3(f"Logged to TensorBoard in {time.time() - start_time:.2f}s")

    @staticmethod
    def move_logs_to_archive_dir() -> None:
        """Move the logs to the archive directory."""
        print("Archiving TensorBoard logs")
        # Ensure archive dir exists
        os.makedirs(TENSORBOARD_LOG_DIR_ARCHIVE, exist_ok=True)
        if os.path.exists(TENSORBOARD_LOG_DIR):
            # Move all files (incl. folders)
            for file in os.listdir(TENSORBOARD_LOG_DIR):
                shutil.move(
                    os.path.join(TENSORBOARD_LOG_DIR, file),
                    os.path.join(TENSORBOARD_LOG_DIR_ARCHIVE, file),
                )
