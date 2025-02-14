from dataclasses import dataclass
from typing import Optional

import numpy as np
from gymnasium import spaces
from sklearn.preprocessing import MinMaxScaler

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import BaseAction
from o2.actions.base_actions.shift_datetime_rule_base_action import (
    ShiftDateTimeRuleAction,
    ShiftDateTimeRuleBaseActionParamsType,
)
from o2.actions.batching_actions.modify_size_of_significant_rule_action import (
    ModifySizeOfSignificantRuleAction,
    ModifySizeOfSignificantRuleActionParamsType,
)
from o2.actions.batching_actions.remove_date_time_rule_action import (
    RemoveDateTimeRuleAction,
    RemoveDateTimeRuleActionParamsType,
)
from o2.models.days import DAYS
from o2.models.settings import Settings
from o2.models.time_period import TimePeriod
from o2.store import Store


@dataclass(frozen=True)
class PPOInput:
    """The PPOInput will be used as an input for the PPO model.

    The following columns/features are defined:

    Continuous features:
        Task:
            - waiting_times, per task
            - idle_time, per task
            - percentage of waiting is batching, per task
            - fixed_cost, per task
            - Percentage of task instances that either have a waiting or idle time, per task

        Resource:
            - waiting_times, per resource
            - available_time, per resource
            - utilization, per resource


        Batching rules:
            - avg_batch_size, per task

    Discrete features:
        - Number of task enablements, per task, per day
        - Number of resources, per task
        - Number of tasks, per resource


    Also we'll have the following actions:
        - Add Batching DateTime Rule, per day, per task,
        - Shift Batching DateTime Rule forward, per task
        - Shift Batching DateTime Rule backward, per task
        - Remove Batching DateTime Rule, per task
        - Add 1h to large waiting time rule, per task
        - Remove 1h from large waiting time rule, per task
        - Add 1h to ready waiting time rule, per task
        - Remove 1h from ready waiting time rule, per task
        - Increase batch size, per task
        - Decrease batch size, per task

    We'll use action masking to disable the invalid actions per step.

    """

    @staticmethod
    def get_observation_space(store: Store) -> spaces.Dict:
        """Get the observation space based on the current state of the store."""
        task_ids = store.current_timetable.get_task_ids()
        num_tasks = len(task_ids)
        num_days = len(DAYS)
        resources = store.current_timetable.get_all_resources()
        num_resources = len(resources)
        num_cases = Settings.NUMBER_OF_CASES or store.current_timetable.total_cases

        high = num_cases * 2

        return spaces.Dict(
            {
                # Continuous resource-related observations
                "resource_waiting_times": spaces.Box(
                    low=0, high=1, shape=(1, num_resources)
                ),
                "resource_available_time": spaces.Box(
                    low=0, high=1, shape=(1, num_resources)
                ),
                "resource_utilization": spaces.Box(
                    low=0, high=1, shape=(1, num_resources)
                ),
                # Discrete resource-related observations
                "resource_num_tasks": spaces.Box(
                    low=0, high=high, shape=(1, num_resources)
                ),
                # Continuous task-related observations
                "task_waiting_times": spaces.Box(low=0, high=1, shape=(1, num_tasks)),
                "task_idle_time": spaces.Box(low=0, high=1, shape=(1, num_tasks)),
                "task_batching_waiting_times_percentage": spaces.Box(
                    low=0, high=1, shape=(1, num_tasks)
                ),
                # Discrete task-related observations
                "task_execution_percentage_with_wt_or_it": spaces.Box(
                    low=0, high=num_cases, shape=(1, num_tasks)
                ),
                "task_enablements_per_day": spaces.Box(
                    low=0, high=num_cases, shape=(1, num_tasks * num_days)
                ),
                "task_num_resources": spaces.Box(
                    low=0, high=num_resources, shape=(1, num_tasks)
                ),
                "task_average_batch_size": spaces.Box(
                    low=0, high=num_resources, shape=(1, num_tasks)
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
            [
                kpis[task_id].waiting_time.total if task_id in kpis else 0
                for task_id in task_ids
            ]
        )

        batching_waiting_times = np.array(
            [
                evaluation.total_batching_waiting_time_per_task.get(task_id, 0)
                for task_id in task_ids
            ]
        )

        batching_waiting_times_percentage = np.array(
            [
                (batching_waiting_times[i] / waiting_times[i])
                if waiting_times[i] != 0
                else 0
                for i in range(len(task_ids))
            ]
        )

        idle_times = np.array(
            [
                kpis[task_id].idle_time.total if task_id in kpis else 0
                for task_id in task_ids
            ]
        )

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times.reshape(1, -1))
        idle_times = scaler_idle_time.fit_transform(idle_times.reshape(1, -1))

        # Discrete features
        task_execution_count_with_wt_or_it_dict = (
            evaluation.task_execution_count_with_wt_or_it
        )
        task_execution_percentage_with_wt_or_it_ = np.array(
            [
                task_execution_count_with_wt_or_it_dict[task_id]
                / evaluation.task_execution_counts[task_id]
                if task_id in task_execution_count_with_wt_or_it_dict
                else 0
                for task_id in task_ids
            ]
        )

        task_enablements_per_day = np.array(
            [
                len(evaluation.task_enablement_weekdays[task_id][day])
                if (
                    task_id in evaluation.task_enablement_weekdays
                    and day in evaluation.task_enablement_weekdays[task_id]
                )
                else 0
                for task_id in task_ids
                for day in DAYS
            ]
        )

        number_of_resources = np.array(
            [
                len(store.current_timetable.get_resources_assigned_to_task(task_id))
                if task_id in task_ids
                else 0
                for task_id in task_ids
            ]
        )

        average_batch_size = np.array(
            [evaluation.avg_batch_size_per_task.get(task_id, 1) for task_id in task_ids]
        )

        return {
            "task_waiting_times": PPOInput._clean_np_array(waiting_times),
            "task_idle_time": PPOInput._clean_np_array(idle_times),
            "task_batching_waiting_times_percentage": PPOInput._clean_np_array(
                batching_waiting_times_percentage
            ),
            "task_execution_percentage_with_wt_or_it": PPOInput._clean_np_array(
                task_execution_percentage_with_wt_or_it_
            ),
            "task_enablements_per_day": PPOInput._clean_np_array(
                task_enablements_per_day
            ),
            "task_num_resources": PPOInput._clean_np_array(number_of_resources),
            "task_average_batch_size": PPOInput._clean_np_array(average_batch_size),
        }

    @staticmethod
    def _get_resource_features(store: Store):
        # TODO: This only uses base resources
        resources = store.base_timetable.get_all_resources()
        evaluation = store.current_evaluation

        # MinMaxScaler for continuous features
        scaler_waiting_time = MinMaxScaler()
        scaler_available_time = MinMaxScaler()
        scaler_utilization = MinMaxScaler()
        scaler_hourly_cost = MinMaxScaler()

        # Continuous features
        waiting_times_dict = evaluation.total_batching_waiting_time_per_resource
        waiting_times = np.array(
            [
                waiting_times_dict[resource.id]  # noqa: SIM401
                if resource.id in waiting_times_dict
                # TODO: 0 might not be the best default value
                else 0
                for resource in resources
            ]
        )

        available_times = np.array(
            [
                evaluation.resource_kpis[resource.id].available_time
                if resource.id in evaluation.resource_kpis
                else 0
                for resource in resources
            ]
        )

        utilizations = np.array(
            [
                evaluation.resource_kpis[resource.id].utilization
                if resource.id in evaluation.resource_kpis
                else 0
                for resource in resources
            ]
        )

        hourly_costs = np.array([resource.cost_per_hour for resource in resources])

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times.reshape(1, -1))
        available_times = scaler_available_time.fit_transform(
            available_times.reshape(1, -1)
        )
        utilizations = scaler_utilization.fit_transform(utilizations.reshape(1, -1))
        hourly_costs = scaler_hourly_cost.fit_transform(hourly_costs.reshape(1, -1))

        # Discrete features
        number_of_tasks = np.array(
            [len(resource.assigned_tasks) for resource in resources]
        )

        return {
            "resource_waiting_times": PPOInput._clean_np_array(waiting_times),
            "resource_available_time": PPOInput._clean_np_array(available_times),
            "resource_utilization": PPOInput._clean_np_array(utilizations),
            "resource_num_tasks": PPOInput._clean_np_array(number_of_tasks),
        }

    @staticmethod
    def get_state_from_store(store: Store) -> dict:
        """Get the input for the PPO model based on the current state of the store."""
        resource_features = PPOInput._get_resource_features(store)
        task_features = PPOInput._get_task_features(store)

        return {
            **resource_features,
            **task_features,
        }

    @staticmethod
    def get_action_space_from_actions(
        actions: list[Optional[BaseAction]],
    ) -> spaces.Discrete:
        """Get the action space based on the actions."""
        return spaces.Discrete(len(actions))

    @staticmethod
    def get_actions_from_store(store: Store) -> list[Optional[BaseAction]]:
        """Get the action based on the index."""
        # TODO: This only uses base resources
        resources = store.base_timetable.get_all_resources()
        current_timetable = store.current_timetable

        actions: list[Optional[BaseAction]] = []

        # TODO: This is not complete
        # - [ ] Add 1h to large waiting time rule (or create), per task
        # - [ ] Remove 1h from large waiting time rule (or remove), per task
        # - [ ] Add 1h to ready waiting time rule (or create), per task
        # - [ ] Remove 1h from ready waiting time rule (or remove), per task
        # - [x] Increase batch size (or create), per task
        # - [x] Decrease batch size (or remove), per task
        # - [x] Add Batching DateTime Rule, per day, per task,
        # - [x] Shift Batching DateTime Rule forward, per day, per task
        # - [x] Shift Batching DateTime Rule backward, per day, per task
        # - [x] Remove Batching DateTime Rule, per day, per task

        for task_id in store.current_timetable.get_task_ids():
            constraints = store.constraints.get_batching_size_rule_constraints(task_id)
            duration_fn = "size" if not constraints else constraints[0].duration_fn
            actions.append(
                ModifySizeOfSignificantRuleAction(
                    ModifySizeOfSignificantRuleActionParamsType(
                        task_id=task_id,
                        change_size=1,
                        duration_fn=duration_fn,
                    )
                )
            )
            actions.append(
                ModifySizeOfSignificantRuleAction(
                    ModifySizeOfSignificantRuleActionParamsType(
                        task_id=task_id,
                        change_size=-1,
                        duration_fn=duration_fn,
                    )
                )
            )
            for day in DAYS:
                # TODO: Is a default value for start and end okay?
                actions.append(
                    AddDateTimeRuleAction(
                        params=AddDateTimeRuleBaseActionParamsType(
                            task_id=task_id,
                            time_period=TimePeriod.from_start_end(
                                day=day, start=12, end=13
                            ),
                            duration_fn=duration_fn,
                        )
                    )
                )
                actions.append(
                    ShiftDateTimeRuleAction(
                        params=ShiftDateTimeRuleBaseActionParamsType(
                            task_id=task_id, day=day, add_to_start=-1, add_to_end=1
                        )
                    )
                )
                actions.append(
                    ShiftDateTimeRuleAction(
                        params=ShiftDateTimeRuleBaseActionParamsType(
                            task_id=task_id, day=day, add_to_start=1, add_to_end=-1
                        )
                    )
                )
                actions.append(
                    RemoveDateTimeRuleAction(
                        params=RemoveDateTimeRuleActionParamsType(
                            task_id=task_id, day=day
                        )
                    )
                )

        return [
            action
            if (
                action is not None
                and store.is_tabu(action) is False
                and action.check_if_valid(store)
            )
            else None
            for action in actions
        ]

    @staticmethod
    def get_action_mask_from_actions(actions: list[Optional[BaseAction]]) -> np.ndarray:
        """Get the action mask based on the actions."""
        mask = np.array([action is not None for action in actions])
        return mask

    @staticmethod
    def _clean_np_array(array: np.ndarray) -> np.ndarray:
        """Clean the numpy array."""
        return np.nan_to_num(array, nan=0, posinf=0, neginf=0).reshape(1, -1)
