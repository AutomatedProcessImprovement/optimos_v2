import io
import os
import shutil
import time
from datetime import datetime

import matplotlib
import tensorflow as tf

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
        """Log the current solution to TensorBoard, including a 2D chart of the Pareto front."""
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
                "current_base/average_batch_size",
                self.store.current_evaluation.average_batch_size_for_batch_enabled_tasks,
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
                "front/max_" + Settings.get_pareto_y_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.max_y,
                step=self.step,
            )

            tf.summary.scalar(
                "front/min_" + Settings.get_pareto_x_label().replace(" ", "_").lower(),
                self.store.current_pareto_front.min_x,
                step=self.step,
            )
            tf.summary.scalar(
                "front/min_" + Settings.get_pareto_y_label().replace(" ", "_").lower(),
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

            if self.step % 100 == 0:
                # --- Plot and log the 2D Pareto front image ---
                fig = self._create_pareto_front_plot()
                image = self._plot_to_image(fig)
                tf.summary.image("pareto_front", image, step=self.step)
                plt.close(fig)

    def _create_pareto_front_plot(self):
        """Create a Matplotlib figure for the Pareto front.

        - Pareto front solution points are plotted in blue.
        - The average point is plotted in green.
        - The base solution is plotted in red.
        """
        fig, ax = plt.subplots(figsize=(16, 9))

        # Plot all Pareto front solution points
        solutions = self.store.current_pareto_front.solutions
        if solutions:
            points = [sol.point for sol in solutions]
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            ax.scatter(xs, ys, c="blue", label="Pareto Front Solutions", alpha=0.7)

        # Plot the base solution
        base_point = self.store.base_solution.point
        if base_point is not None:
            ax.scatter(
                base_point[0],
                base_point[1],
                c="red",
                marker="D",
                s=100,
                label="Base Solution",
            )
        # Plot the average point
        avg_point = self.store.current_pareto_front.avg_point
        if avg_point is not None:
            ax.scatter(
                avg_point[0],
                avg_point[1],
                c="green",
                marker="x",
                s=100,
                label="Average Point",
            )
            # If using Simulated Annealing, draw a circle around the average point with radius equal to self.agent.temperature
            if isinstance(self.agent, SimulatedAnnealingAgent):
                # Save current axis limits to prevent zooming out when adding the circle.
                current_xlim = ax.get_xlim()
                current_ylim = ax.get_ylim()
                circle = plt.Circle(
                    (avg_point[0], avg_point[1]),
                    self.agent.temperature,
                    color="purple",
                    fill=False,
                    linestyle="--",
                    clip_on=True,
                )
                ax.add_patch(circle)
                # Restore the original axis limits.
                ax.set_xlim(current_xlim)
                ax.set_ylim(current_ylim)
                # Create a legend patch for the SA radius.
                import matplotlib.patches as mpatches

                sa_patch = mpatches.Patch(
                    edgecolor="purple",
                    facecolor="none",
                    linestyle="--",
                    label="SA Radius",
                )

        # Combine legend handles, including the SA radius patch if applicable
        handles, labels = ax.get_legend_handles_labels()
        if isinstance(self.agent, SimulatedAnnealingAgent) and avg_point is not None:
            handles.append(sa_patch)  # type: ignore
            labels.append("SA Radius")
        ax.legend(handles, labels)

        # Set the axis labels using settings (if available)
        ax.set_xlabel(Settings.get_pareto_x_label())
        ax.set_ylabel(Settings.get_pareto_y_label())
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def _plot_to_image(self, figure):
        """Convert the Matplotlib figure to a PNG image and returns it as a tensor."""
        buf = io.BytesIO()
        figure.savefig(buf, format="png", dpi=50)
        buf.seek(0)
        # Convert PNG buffer to TF image
        image = tf.image.decode_png(buf.getvalue(), channels=4)
        # Add the batch dimension
        image = tf.expand_dims(image, 0)
        return image

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
