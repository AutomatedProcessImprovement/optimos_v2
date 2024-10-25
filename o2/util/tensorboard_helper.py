import tensorflow as tf

from o2.agents.agent import Agent
from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.models.solution import Solution
from o2.store import Store

log_dir = "./logs/progress_tensorboard"


# TODO make this a singleton, I can access anywhere!
class TensorBoardHelper:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.store = self.agent.store
        self.writer = tf.summary.create_file_writer(
            log_dir, name=self.store.settings.agent
        )
        self.step = 0

    def tensor_board_iteration_callback(self, solution: Solution) -> None:
        """This method is used to log the current solution to tensorboard."""
        with self.writer.as_default():
            self.step += 1
            if self.agent is SimulatedAnnealingAgent:
                tf.summary.scalar("temperature", self.agent.temperature, step=self.step)
