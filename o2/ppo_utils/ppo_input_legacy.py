from dataclasses import dataclass
from typing import Optional

import numpy as np
from gymnasium import spaces
from sklearn.preprocessing import MinMaxScaler

from o2.actions.base_actions.base_action import BaseAction
from o2.actions.base_actions.modify_calendar_base_action import (
    ModifyCalendarBaseActionParamsType,
)
from o2.actions.base_actions.modify_resource_base_action import (
    ModifyResourceBaseActionParamsType,
)
from o2.actions.legacy_optimos_actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.legacy_optimos_actions.remove_resource_by_cost_action import (
    RemoveResourceByCostAction,
)
from o2.models.days import DAYS
from o2.models.settings import Settings
from o2.store import Store


@dataclass(frozen=True)
class PPOInputLegacy:
    """The PPOInputLegacy will be used as an input for the PPO model.

    This legacy variant almost exclusively is made for the legacy optimos,
    with no regard to batching.

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
        num_cases = Settings.NUMBER_OF_CASES or store.current_timetable.total_cases

        high = num_cases * 2

        return spaces.Dict(
            {
                # Continuous resource-related observations
                "resource_waiting_times": spaces.Box(low=0, high=1, shape=(num_resources, 1)),
                "resource_available_time": spaces.Box(low=0, high=1, shape=(num_resources, 1)),
                "resource_utilization": spaces.Box(low=0, high=1, shape=(num_resources, 1)),
                "resource_hourly_cost": spaces.Box(low=0, high=1, shape=(num_resources, 1)),
                # Discrete resource-related observations
                "resource_num_tasks": spaces.Box(low=0, high=high, shape=(num_resources, 1)),
                # Continuous task-related observations
                "task_waiting_times": spaces.Box(low=0, high=1, shape=(num_tasks, 1)),
                "task_idle_time": spaces.Box(low=0, high=1, shape=(num_tasks, 1)),
                # Discrete task-related observations
                "task_execution_count_with_wt_or_it": spaces.Box(low=0, high=num_cases, shape=(num_tasks, 1)),
                "task_execution_counts": spaces.Box(low=0, high=num_cases, shape=(num_tasks, 1)),
                "task_num_resources": spaces.Box(low=0, high=num_resources, shape=(num_tasks, 1)),
            }
        )

    @staticmethod
    def _get_task_features(store: Store) -> dict[str, np.ndarray]:
        task_ids = store.current_timetable.get_task_ids()
        kpis = store.current_evaluation.task_kpis
        evaluation = store.current_evaluation

        # MinMaxScaler for continuous features
        scaler_waiting_time = MinMaxScaler()
        scaler_idle_time = MinMaxScaler()

        # Continuous features
        waiting_times = np.array([kpis[task_id].waiting_time.total for task_id in task_ids]).reshape(-1, 1)

        idle_times = np.array([kpis[task_id].idle_time.total for task_id in task_ids]).reshape(-1, 1)

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times)
        idle_times = scaler_idle_time.fit_transform(idle_times)

        # Discrete features
        task_execution_count_with_wt_or_it_dict = evaluation.task_execution_count_with_wt_or_it
        task_execution_count_with_wt_or_it_ = np.array(
            [task_execution_count_with_wt_or_it_dict.get(task_id, 0) for task_id in task_ids]
        ).reshape(-1, 1)

        task_execution_counts_dict = evaluation.task_execution_counts
        task_execution_counts = np.array(
            [task_execution_counts_dict.get(task_id, 0) for task_id in task_ids]
        ).reshape(-1, 1)

        number_of_resources = np.array(
            [
                len(store.current_timetable.get_resources_assigned_to_task(task_id))
                if task_id in task_ids
                else 0
                for task_id in task_ids
            ]
        ).reshape(-1, 1)

        return {
            "task_waiting_times": waiting_times,
            "task_idle_time": idle_times,
            "task_execution_count_with_wt_or_it": task_execution_count_with_wt_or_it_,
            "task_execution_counts": task_execution_counts,
            "task_num_resources": number_of_resources,
        }

    @staticmethod
    def _get_resource_features(store: Store) -> dict[str, np.ndarray]:
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
                waiting_times_dict[resource.id]
                if resource.id in waiting_times_dict
                # TODO: 0 might not be the best default value
                else 0
                for resource in resources
            ]
        ).reshape(-1, 1)

        available_times = np.array(
            [
                evaluation.resource_kpis[resource.id].available_time
                if resource.id in evaluation.resource_kpis
                else 0
                for resource in resources
            ]
        ).reshape(-1, 1)

        utilizations = np.array(
            [
                evaluation.resource_kpis[resource.id].utilization
                if resource.id in evaluation.resource_kpis
                else 0
                for resource in resources
            ]
        ).reshape(-1, 1)

        hourly_costs = np.array([resource.cost_per_hour for resource in resources]).reshape(-1, 1)

        # Scale continuous features
        waiting_times = scaler_waiting_time.fit_transform(waiting_times)
        available_times = scaler_available_time.fit_transform(available_times)
        utilizations = scaler_utilization.fit_transform(utilizations)
        hourly_costs = scaler_hourly_cost.fit_transform(hourly_costs)

        # Discrete features
        number_of_tasks = np.array([len(resource.assigned_tasks) for resource in resources]).reshape(-1, 1)

        return {
            "resource_waiting_times": waiting_times,
            "resource_available_time": available_times,
            "resource_utilization": utilizations,
            "resource_hourly_cost": hourly_costs,
            "resource_num_tasks": number_of_tasks,
        }

    @staticmethod
    def get_state_from_store(store: Store) -> dict:
        """Get the input for the PPO model based on the current state of the store."""
        resource_features = PPOInputLegacy._get_resource_features(store)
        task_features = PPOInputLegacy._get_task_features(store)

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

        actions = []

        # - Add Hour to start of calendar, per resource, per day
        # - Add Hour to end of calendar, per resource, per day
        # - Remove first hour from calendar, per resource, per day
        # - Remove last hour from calendar, per resource, per day
        # - Shift Hour forward in calendar, per resource, per day
        # - Shift Hour backward in calendar, per resource, per day
        # - Clone resource, per resource
        # - Remove resource, per resource
        modify_calendar_action_params: list[Optional[ModifyCalendarBaseActionParamsType]] = []

        modify_resource_action_params: list[Optional[ModifyResourceBaseActionParamsType]] = []

        for resource in resources:
            if current_timetable.get_resource(resource.id) is None:
                modify_resource_action_params.extend([None] * ((len(DAYS) * 6) + 2))
                continue
            modify_resource_action_params.extend(
                [
                    # Clone resource
                    ModifyResourceBaseActionParamsType(
                        resource_id=resource.id,
                        clone_resource=True,
                    ),
                    # Remove resource
                    ModifyResourceBaseActionParamsType(
                        resource_id=resource.id,
                        remove_resource=True,
                    ),
                ]
            )
            calendar = store.current_timetable.get_calendar_for_resource(resource.id)
            for day in DAYS:
                if calendar is None:
                    modify_calendar_action_params.extend([None] * 6)
                    continue
                periods = calendar.get_periods_for_day(day)
                if periods is None or len(periods) == 0:
                    modify_calendar_action_params.extend([None] * 6)
                    continue
                # Remove first hour
                modify_calendar_action_params.extend(
                    [
                        # Add Hour to start of calendar
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[0].id,
                            day=day,
                            add_hours_before=1,
                        ),
                        # Add Hour to end of calendar
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[-1].id,
                            day=day,
                            add_hours_after=1,
                        ),
                        # Remove first hour
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[0].id,
                            day=day,
                            remove_period=True,
                        ),
                        # Remove last hour
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[-1].id,
                            day=day,
                            remove_period=True,
                        ),
                        # Shift Hour forward
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[0].id,
                            day=day,
                            shift_hours=1,
                        ),
                        # Shift Hour backward
                        ModifyCalendarBaseActionParamsType(
                            calendar_id=calendar.id,
                            period_id=periods[-1].id,
                            day=day,
                            shift_hours=-1,
                        ),
                    ]
                )
        actions: list[Optional[BaseAction]] = [
            # TODO: We'll use a ModifyCalendarByCostAction for now
            ModifyCalendarByCostAction(modify_calendar_action_param) if modify_calendar_action_param else None
            for modify_calendar_action_param in modify_calendar_action_params
        ]
        actions.extend(
            [
                # TODO: We'll use a RemoveResourceByCostAction for now
                RemoveResourceByCostAction(modify_resource_action_param)
                if modify_resource_action_param
                else None
                for modify_resource_action_param in modify_resource_action_params
            ]
        )
        return [
            action if (action is not None and store.is_tabu(action) is False) else None for action in actions
        ]

    @staticmethod
    def get_action_mask_from_actions(actions: list[Optional[BaseAction]]) -> np.ndarray:
        """Get the action mask based on the actions."""
        mask = np.array([action is not None for action in actions])
        return mask
