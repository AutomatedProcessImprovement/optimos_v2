from dataclasses import dataclass

import numpy as np
from gym import Space, spaces
from sklearn.preprocessing import MinMaxScaler

from o2.models.days import DAYS
from o2.models.evaluation import Evaluation
from o2.store import Store


@dataclass(frozen=True)
class PPOInput:
    """The PPOInput will be used as an input for the PPO model.

    The following columns/features are defined:

    Continuous features:
        Task:
            - waiting_times, per task
            - idle_time, per task
        Resource:
            - waiting_times, per resource
            - available_time, per resource
            - utilization, per resource
            - hourly_cost, per resource
        Batching rules:
            - Abs. waiting time difference after removal ("impact"), per batching rule


    Discrete features:
    - Number of task instances that either have a waiting or idle time, per task
    - Number of task enablements, per task, per day
    - Number of resources, per task
    - Number of tasks, per resource



    Also we'll have the following actions:
    - Add Hour to calendar, per resource, per day
    - Remove Hour from calendar, per resource, per day
    - Shift Hour forward in calendar, per resource, per day
    - Shift Hour backward in calendar, per resource, per day
    - Clone resource, per resource

    We'll use action masking to disable the invalid actions per step.

    """

    @staticmethod
    def get_observation_space(store: Store) -> spaces.Dict:
        """Get the observation space based on the current state of the store."""
        task_ids = store.current_timetable.get_task_ids()
        num_tasks = len(task_ids)
        resources = store.current_timetable.get_all_resources()
        num_resources = len(resources)
        num_cases = store.settings.num_of_cases

        high = store.settings.num_of_cases * 2

        return spaces.Dict(
            {
                "continuous": spaces.Dict(
                    {
                        "task": spaces.Dict(
                            {
                                "waiting_times": spaces.Box(
                                    low=0, high=1, shape=(num_tasks, 1)
                                ),
                                "idle_time": spaces.Box(
                                    low=0, high=1, shape=(num_tasks, 1)
                                ),
                            }
                        ),
                        "resource": spaces.Dict(
                            {
                                "waiting_times": spaces.Box(
                                    low=0, high=1, shape=(num_resources, 1)
                                ),
                                "available_time": spaces.Box(
                                    low=0, high=1, shape=(num_resources, 1)
                                ),
                                "utilization": spaces.Box(
                                    low=0, high=1, shape=(num_resources, 1)
                                ),
                                "hourly_cost": spaces.Box(
                                    low=0, high=1, shape=(num_resources, 1)
                                ),
                            }
                        ),
                    }
                ),
                "discrete": spaces.Dict(
                    {
                        "task": spaces.Dict(
                            {
                                "task_execution_count_with_wt_or_it": spaces.Box(
                                    low=0, high=num_cases, shape=(num_tasks, 1)
                                ),
                                "task_execution_counts": spaces.Box(
                                    low=0, high=num_cases, shape=(num_tasks, 1)
                                ),
                                "num_resources": spaces.Box(
                                    low=0, high=num_resources, shape=(num_tasks, 1)
                                ),
                            }
                        ),
                        "resource": spaces.Dict(
                            {
                                "num_tasks": spaces.Box(
                                    low=0, high=high, shape=(num_tasks, 1)
                                ),
                            }
                        ),
                    }
                ),
            }
        )

    @staticmethod
    def _get_task_features(store: Store):
        task_ids = store.current_timetable.get_task_ids()
        kpis = store.current_evaluation.task_kpis
        evaluation = store.current_evaluation

        # MinMaxScaler for continuous features
        scaler_waiting_time = MinMaxScaler()
        scaler_idle_time = MinMaxScaler()

        # Continuous features
        waiting_times = np.array(
            [kpis[task_id].waiting_time.total for task_id in task_ids]
        ).reshape(-1, 1)

        idle_times = np.array(
            [kpis[task_id].idle_time.total for task_id in task_ids]
        ).reshape(-1, 1)

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times)
        idle_times = scaler_idle_time.fit_transform(idle_times)

        # Discrete features
        task_execution_count_with_wt_or_it_dict = (
            evaluation.get_task_execution_count_with_wt_or_it()
        )
        task_execution_count_with_wt_or_it_ = np.array(
            [task_execution_count_with_wt_or_it_dict[task_id] for task_id in task_ids]
        ).reshape(-1, 1)

        task_execution_counts_dict = evaluation.get_task_execution_counts()
        task_execution_counts = np.array(
            [task_execution_counts_dict[task_id] for task_id in task_ids]
        ).reshape(-1, 1)

        number_of_resources = np.array(
            [
                len(store.current_timetable.get_resources_assigned_to_task(task_id))
                for task_id in task_ids
            ]
        ).reshape(-1, 1)

        return {
            "continuous": {
                "waiting_times": waiting_times,
                "idle_time": idle_times,
            },
            "discrete": {
                "task_execution_count_with_wt_or_it": task_execution_count_with_wt_or_it_,
                "task_execution_counts": task_execution_counts,
                "num_resources": number_of_resources,
            },
        }

    @staticmethod
    def _get_resource_features(store: Store):
        resources = store.current_timetable.get_all_resources()
        evaluation = store.current_evaluation

        # MinMaxScaler for continuous features
        scaler_waiting_time = MinMaxScaler()
        scaler_available_time = MinMaxScaler()
        scaler_utilization = MinMaxScaler()
        scaler_hourly_cost = MinMaxScaler()

        # Continuous features
        waiting_times_dict = evaluation.waiting_time_per_resource
        waiting_times = np.array(
            [waiting_times_dict[resource.id] for resource in resources]
        ).reshape(-1, 1)

        available_times = np.array(
            [
                evaluation.resource_kpis[resource.id].available_time.total
                for resource in resources
            ]
        ).reshape(-1, 1)

        utilizations = np.array(
            [
                evaluation.resource_kpis[resource.id].utilization.total
                for resource in resources
            ]
        ).reshape(-1, 1)

        hourly_costs = np.array(
            [resource.cost_per_hour for resource in resources]
        ).reshape(-1, 1)

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times)
        available_times = scaler_available_time.fit_transform(available_times)
        utilizations = scaler_utilization.fit_transform(utilizations)
        hourly_costs = scaler_hourly_cost.fit_transform(hourly_costs)

        # Discrete features
        number_of_tasks = np.array(
            [len(resource.assigned_tasks) for resource in resources]
        ).reshape(-1, 1)

        return {
            "continuous": {
                "waiting_times": waiting_times,
                "available_time": available_times,
                "utilization": utilizations,
                "hourly_cost": hourly_costs,
            },
            "discrete": {"num_tasks": number_of_tasks},
        }

    @staticmethod
    def state_from_store(store: Store) -> dict:
        """Get the input for the PPO model based on the current state of the store."""
        task_features = PPOInput._get_task_features(store)
        resource_features = PPOInput._get_resource_features(store)

        return {
            "continuous": {
                "task": task_features["continuous"],
                "resource": resource_features["continuous"],
            },
            "discrete": {
                "task": task_features["discrete"],
                "resource": resource_features["discrete"],
            },
        }

    @staticmethod
    def action_space_from_store(store: Store) -> spaces.Discrete:
        """Get the action space based on the current state of the store."""
        resources = store.current_timetable.get_all_resources()
        num_days = len(DAYS)

        # - Add Hour to calendar, per resource, per day
        # - Remove Hour from calendar, per resource, per day
        # - Shift Hour forward in calendar, per resource, per day
        # - Shift Hour backward in calendar, per resource, per day
        # - Clone resource, per resource

        num_actions = (
            len(resources) * num_days * 4  # Add, Remove, Shift Forward, Shift Backward
            + len(resources)  # Clone resource
        )

        return spaces.Discrete(num_actions)
