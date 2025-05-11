"""TimetableType is the main class for modeling timetables."""

import operator
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Callable, Literal, Optional, Union

from dataclass_wizard import JSONWizard

from o2.models.days import DAY
from o2.models.timetable.batch_type import BATCH_TYPE
from o2.models.timetable.batching_rule import BatchingRule
from o2.models.timetable.firing_rule import FiringRule
from o2.models.timetable.gateway_branching_probability import GatewayBranchingProbability
from o2.models.timetable.granule_size import GranuleSize
from o2.models.timetable.multitask import Multitask
from o2.models.timetable.resource import Resource
from o2.models.timetable.resource_calendar import ResourceCalendar
from o2.models.timetable.resource_pool import ResourcePool
from o2.models.timetable.rule_type import RULE_TYPE
from o2.models.timetable.task_resource_distribution import (
    ArrivalTimeDistribution,
    TaskResourceDistributions,
)
from o2.models.timetable.time_period import TimePeriod
from o2.util.custom_dumper import CustomDumper, CustomLoader
from o2.util.helper import (
    cached_lambdify,
    hash_int,
    name_is_clone_of,
)
from o2.util.logger import info

if TYPE_CHECKING:
    from o2.models.constraints import ConstraintsType
    from o2.models.rule_selector import RuleSelector
    from o2.models.state import State


@dataclass(frozen=True, eq=True)
class TimetableType(JSONWizard, CustomLoader, CustomDumper):
    """The main class representing the timetable."""

    resource_profiles: list[ResourcePool]
    arrival_time_distribution: ArrivalTimeDistribution
    arrival_time_calendar: list["TimePeriod"]
    gateway_branching_probabilities: list[GatewayBranchingProbability]
    task_resource_distribution: list[TaskResourceDistributions]
    resource_calendars: list[ResourceCalendar]
    batch_processing: list[BatchingRule] = field(default_factory=list)
    start_time: str = "2000-01-01T00:00:00Z"
    total_cases: int = 1000
    multitask: Optional[Multitask] = None
    model_type: Optional[Literal["FUZZY", "CRISP"]] = None
    granule_size: Optional[GranuleSize] = None
    event_distribution: Optional[list[dict] | dict] = None
    global_attributes: Optional[list[dict]] = None
    case_attributes: Optional[list[dict]] = None
    event_attributes: Optional[list[dict]] = None
    branch_rules: Optional[list[dict]] = None

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        skip_defaults = True

    def init_fixed_cost_fns(self, constraints: "ConstraintsType") -> "TimetableType":
        """Initialize the fixed cost fn for all resources."""
        return replace(
            self,
            resource_profiles=[
                replace(
                    resource_profile,
                    fixed_cost_fn=constraints.get_fixed_cost_fn_for_task(resource_profile.id),
                )
                for resource_profile in self.resource_profiles
            ],
        )

    def get_batching_rule(
        self, rule_selector: "RuleSelector"
    ) -> Union[tuple[int, BatchingRule], tuple[None, None]]:
        """Get a batching rule by rule selector."""
        return next(
            (
                (i, rule)
                for i, rule in enumerate(self.batch_processing)
                if rule.task_id == rule_selector.batching_rule_task_id
            ),
            (
                None,
                None,
            ),
        )

    def get_batching_rules_for_task(
        self, task_id: str, batch_type: Optional["BATCH_TYPE"] = None
    ) -> list[BatchingRule]:
        """Get all batching rules for a task."""
        return [
            rule
            for rule in self.batch_processing
            if rule.task_id == task_id and (batch_type is None or rule.type == batch_type)
        ]

    def get_batching_rules_for_tasks(
        self, task_ids: list[str], batch_type: Optional["BATCH_TYPE"] = None
    ) -> list[BatchingRule]:
        """Get all batching rules for a list of tasks."""
        return [
            rule
            for rule in self.batch_processing
            if rule.task_id in task_ids and (batch_type is None or rule.type == batch_type)
        ]

    def get_firing_rules_for_task(
        self,
        task_id: str,
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list[FiringRule]:
        """Get all firing rules for a task."""
        return [
            firing_rule
            for batching_rule in self.get_batching_rules_for_tasks([task_id], batch_type)
            for firing_rules in batching_rule.firing_rules
            for firing_rule in firing_rules
            if rule_type is None or firing_rule.attribute == rule_type
        ]

    def get_longest_time_period_for_daily_hour_firing_rules(
        self, task_id: str, day: DAY
    ) -> Optional[tuple[Optional["RuleSelector"], "RuleSelector", "RuleSelector"]]:
        """Get the longest time period for daily hour firing rules.

        Returns the Rule Selector of the day, lower bound, and upper bound.
        """

        batching_rules = self.get_batching_rules_for_task(
            task_id=task_id,
        )

        best_selector = None
        best_length = 0

        for batching_rule in batching_rules:
            if batching_rule is None:
                continue
            periods = batching_rule.get_time_period_for_daily_hour_firing_rules().items()
            for (day_selector, lower_bound_selector, upper_bound_selector), (
                _day,
                lower_bound,
                upper_bound,
            ) in periods:
                if _day == day:
                    length = (
                        (upper_bound - lower_bound)
                        if upper_bound is not None and lower_bound is not None
                        else 0
                    )
                    if length > best_length:
                        best_selector = (
                            day_selector,
                            lower_bound_selector,
                            upper_bound_selector,
                        )
                        best_length = length
        return best_selector

    def get_firing_rule_selectors_for_task(
        self,
        task_id: str,
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list["RuleSelector"]:
        """Get all firing rule selectors for a task."""
        return [
            rule_selector
            for batching_rule in self.get_batching_rules_for_tasks([task_id], batch_type)
            for rule_selector in batching_rule.get_firing_rule_selectors(rule_type)
        ]

    def get_firing_rule_selectors_for_tasks(
        self,
        task_ids: list[str],
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list["RuleSelector"]:
        """Get all firing rule selectors for a list of tasks."""
        return [
            rule_selector
            for batching_rule in self.get_batching_rules_for_tasks(task_ids, batch_type)
            for rule_selector in batching_rule.get_firing_rule_selectors(rule_type)
        ]

    def get_firing_rules_for_tasks(
        self,
        task_ids: list[str],
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list[FiringRule]:
        """Get all firing rules for a list of tasks."""
        return [
            firing_rule
            for batching_rule in self.get_batching_rules_for_tasks(task_ids, batch_type)
            for firing_rules in batching_rule.firing_rules
            for firing_rule in firing_rules
            if rule_type is None or firing_rule.attribute == rule_type
        ]

    def get_resource(self, resource_name: str) -> Optional[Resource]:
        """Get resource (from resource_profiles) with the given name.

        Looks through all resource profiles and returns the first resource,
        that matches the given id.
        """
        for resource_profile in self.resource_profiles:
            for resource in resource_profile.resource_list:
                # For compatibility with legacy Optimos, we also check for the
                # resource name with "timetable" appended.
                if (
                    resource.name == resource_name
                    or resource.id == (resource_name + "timetable")
                    or (resource.id + "timetable") == resource_name
                ):
                    return resource
        return None

    def get_tasks(self, resource_id: str) -> list[str]:
        """Get all tasks assigned to a resource."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return []
        return resource.assigned_tasks

    def get_task_resource_distribution(self, task_id: str) -> Optional[TaskResourceDistributions]:
        """Get task resource distribution by task id."""
        for task_resource_distribution in self.task_resource_distribution:
            if task_resource_distribution.task_id == task_id:
                return task_resource_distribution
        return None

    def get_resources_assigned_to_task(self, task_id: str) -> list[str]:
        """Get all resources assigned to a task."""
        task_resource_distribution = self.get_task_resource_distribution(task_id)
        if task_resource_distribution is None:
            return []
        return [resource.resource_id for resource in task_resource_distribution.resources]

    def get_task_ids_assigned_to_resource(self, resource_id: str) -> list[str]:
        """Get all tasks assigned to a resource."""
        return [
            task_resource_distribution.task_id
            for task_resource_distribution in self.task_resource_distribution
            if resource_id in task_resource_distribution.resource_ids
        ]

    def get_resource_profiles_containing_resource(self, resource_id: str) -> list[ResourcePool]:
        """Get the resource profiles containing a resource."""
        return [
            resource_profile
            for resource_profile in self.resource_profiles
            if any(resource.id == resource_id for resource in resource_profile.resource_list)
        ]

    def get_resource_profile(self, profile_id: str) -> Optional[ResourcePool]:
        """Get a resource profile by profile id.

        Legacy Optimos considers the profile id to be a task id.
        """
        return next(
            (
                resource_profile
                for resource_profile in self.resource_profiles
                if resource_profile.id == profile_id
            ),
            None,
        )

    def get_resource_calendar_id(self, resource_id: str) -> Optional[str]:
        """Get the resource calendar id for a resource."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return None
        return resource.calendar

    def get_hourly_rates(self) -> dict[str, int]:
        """Get the cost per hour for each resource."""
        return {resource.id: resource.cost_per_hour for resource in self.get_all_resources()}

    def get_fixed_cost_fns(self) -> dict[str, Callable[[float], float]]:
        """Get the fixed cost function for each resource pool (task)."""
        return {
            resource_profile.id: cached_lambdify(resource_profile.fixed_cost_fn)
            for resource_profile in self.resource_profiles
        }

    def get_calendar_for_resource(self, resource_name: str) -> Optional[ResourceCalendar]:
        """Get a resource calendar by resource name."""
        calendar_id = self.get_resource_calendar_id(resource_name)
        if calendar_id is None:
            return None
        return self.get_calendar(calendar_id)

    def get_calendar_for_base_resource(self, resource_id: str) -> Optional[ResourceCalendar]:
        """Get a resource calendar by resource clone/original name.

        If the resource is a clone, get the calendar of the base resource.
        """
        return next(
            (
                self.get_calendar(resource.calendar)
                for resource in self.resource_profiles
                for resource in resource.resource_list
                if resource.id == resource_id or name_is_clone_of(resource_id, resource.id)
            ),
            None,
        )

    def get_calendars_for_resource_clones(self, resource_name: str) -> list[ResourceCalendar]:
        """Get all resource calendars of clones of a resource."""
        return [
            resource_calendar
            for resource_calendar in self.resource_calendars
            if name_is_clone_of(resource_calendar.name, resource_name)
        ]

    def get_calendar(self, calendar_id: str) -> Optional[ResourceCalendar]:
        """Get a resource calendar by calendar id."""
        for resource_calendar in self.resource_calendars:
            if resource_calendar.id == calendar_id:
                return resource_calendar
        return None

    def get_all_resources(self) -> list[Resource]:
        """Get all resources."""
        resources = {
            resource.id: resource
            for resource_profile in self.resource_profiles
            for resource in resource_profile.resource_list
        }
        return list(resources.values())

    def get_deleted_resources(self, base_state: "State") -> list[Resource]:
        """Get all resources that have been deleted."""
        return [
            resource
            for resource_profile in base_state.timetable.resource_profiles
            for resource in resource_profile.resource_list
            if self.get_resource(resource.id) is None
        ]

    def get_resources_with_cost(self) -> list[tuple[Resource, int]]:
        """Get all resources with cost. Sorted desc."""
        return sorted(
            (
                (
                    resource_profile,
                    resource_profile.get_total_cost(self),
                )
                for resource_profile in self.get_all_resources()
            ),
            key=operator.itemgetter(1),
            reverse=True,
        )

    def replace_batching_rule(
        self, rule_selector: "RuleSelector", new_batching_rule: BatchingRule
    ) -> "TimetableType":
        """Replace a batching rule."""
        return replace(
            self,
            batch_processing=[
                new_batching_rule if rule.task_id == rule_selector.batching_rule_task_id else rule
                for rule in self.batch_processing
            ],
        )

    def replace_firing_rule(
        self, rule_selector: "RuleSelector", new_firing_rule: FiringRule, duration_fn: Optional[str] = None
    ) -> "TimetableType":
        """Replace a firing rule."""
        _, batching_rule = self.get_batching_rule(rule_selector)
        if batching_rule is None:
            return self
        new_batching_rule = batching_rule.replace_firing_rule(
            rule_selector, new_firing_rule, duration_fn=duration_fn
        )
        return self.replace_batching_rule(rule_selector, new_batching_rule)

    def add_firing_rule(
        self,
        rule_selector: "RuleSelector",
        new_firing_rule: FiringRule,
        duration_fn: Optional[str] = None,
    ) -> "TimetableType":
        """Add a firing rule."""
        _, old_batching_rule = self.get_batching_rule(rule_selector)
        if old_batching_rule is None:
            batching_rule = BatchingRule.from_task_id(
                rule_selector.batching_rule_task_id,
                firing_rules=[new_firing_rule],
                duration_fn=duration_fn,
            )
            return replace(self, batch_processing=self.batch_processing + [batching_rule])
        else:
            batching_rule = old_batching_rule.add_firing_rule(new_firing_rule)
            return self.replace_batching_rule(rule_selector, batching_rule)

    def replace_resource_calendar(self, new_calendar: ResourceCalendar) -> "TimetableType":
        """Replace a resource calendar. Returns a new TimetableType."""
        resource_calendars = [
            new_calendar if rc.id == new_calendar.id else rc for rc in self.resource_calendars
        ]
        return replace(self, resource_calendars=resource_calendars)

    def remove_resource(self, resource_id: str) -> "TimetableType":
        """Get a new timetable with a resource removed."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return self

        new_resource_profiles = [
            resource_profile.remove_resource(resource_id) for resource_profile in self.resource_profiles
        ]

        new_task_resource_distribution = [
            task_resource_distribution.remove_resource(resource_id)
            for task_resource_distribution in self.task_resource_distribution
        ]

        new_resource_calendars = [
            resource_calendar
            for resource_calendar in self.resource_calendars
            if resource_calendar.id != resource.calendar
        ]

        return replace(
            self,
            resource_profiles=new_resource_profiles,
            task_resource_distribution=new_task_resource_distribution,
            resource_calendars=new_resource_calendars,
        )

    def clone_resource(self, resource_id: str, assigned_tasks: Optional[list[str]]) -> "TimetableType":
        """Get a new timetable with a resource duplicated.

        The new resource will only have the assigned tasks given,
        but copy all other properties from the original resource.

        The Clone will be added in three places:
        1. in the resource calendars
        2. in the resource pools of the assigned_tasks
        3. in the task_resource_distribution of the assigned_tasks

        The Resource Constraints will not be cloned, because the original
        constraints will automatically be "assigned" based on the name.

        The Naming of the resource will also reflect clones of clones,
        meaning a clone of a clone will have the same name to a first level clone
        """
        original_resource = self.get_resource(resource_id)
        if original_resource is None:
            return self
        if assigned_tasks is None:
            assigned_tasks = original_resource.assigned_tasks
        resource_clone = original_resource.clone(assigned_tasks)

        cloned_resource_calendars = self._clone_resource_calendars(
            original_resource, resource_clone, assigned_tasks
        )

        cloned_resource_profiles = self._clone_resource_profiles(
            original_resource, resource_clone, assigned_tasks
        )

        cloned_resource_distribution = self._clone_task_distributions(
            original_resource, resource_clone, assigned_tasks
        )
        return replace(
            self,
            resource_profiles=cloned_resource_profiles,
            task_resource_distribution=cloned_resource_distribution,
            resource_calendars=cloned_resource_calendars,
        )

    def remove_task_from_resource(self, resource_id: str, task_id: str) -> "TimetableType":
        """Get a new timetable with a task removed from a resource.

        The task will be removed from the resource's assigned tasks.
        The resource will be removed from the task's resource distribution.
        """
        resource = self.get_resource(resource_id)
        if resource is None:
            return self

        updated_resource = resource.remove_task(task_id)

        new_resource_profiles = [
            resource_profile.remove_resource(resource_id)
            if resource_profile.id == task_id
            else resource_profile.update_resource(updated_resource)
            for resource_profile in self.resource_profiles
        ]

        new_task_resource_distribution = [
            task_resource_distribution.remove_resource(resource_id)
            if task_resource_distribution.task_id == task_id
            else task_resource_distribution
            for task_resource_distribution in self.task_resource_distribution
        ]

        return replace(
            self,
            resource_profiles=new_resource_profiles,
            task_resource_distribution=new_task_resource_distribution,
        )

    def get_task_ids(self) -> list[str]:
        """Get all task ids."""
        return [task.task_id for task in self.task_resource_distribution]

    def get_highest_availability_time_period(self, task_id: str, min_hours: int) -> Optional[TimePeriod]:
        """Get the highest availability time period for the task.

        The highest availability time period is the time period with the highest
        frequency of availability.
        """
        task_distribution = self.get_task_resource_distribution(task_id)
        if task_distribution is None:
            return None
        return task_distribution.get_highest_availability_time_period(self, min_hours)

    @property
    def max_total_hours_per_resource(self) -> int:
        """Get the maximum total hours per resource."""
        return max(resource_calendar.total_hours for resource_calendar in self.resource_calendars)

    @property
    def max_consecutive_hours_per_resource(self) -> int:
        """Get the maximum shift size per resource."""
        return max(resource_calendar.max_consecutive_hours for resource_calendar in self.resource_calendars)

    @property
    def max_periods_per_day_per_resource(self) -> int:
        """Get the maximum shifts per day per resource."""
        return max(resource_calendar.max_periods_per_day for resource_calendar in self.resource_calendars)

    @property
    def batching_rules_exist(self) -> bool:
        """Check if any batching rules exist."""
        return len(self.batch_processing) > 0

    def _clone_resource_calendars(self, original: Resource, clone: Resource, _: list[str]):
        """Get a Clone of the Resource Calendars, with the new resource added."""
        original_resource_calendar = self.get_calendar(original.calendar)
        if original_resource_calendar is None:
            return self.resource_calendars

        return self.resource_calendars + [
            replace(
                original_resource_calendar,
                id=clone.calendar,
                name=clone.calendar,
            )
        ]

    def _clone_task_distributions(
        self,
        original: Resource,
        clone: Resource,
        assigned_tasks: list[str],
    ):
        """Get a Clone of the Task Distributions, with the new resource added."""
        original_task_distributions = [
            self.get_task_resource_distribution(task_id) for task_id in assigned_tasks
        ]

        new_task_distributions = [
            task_distribution.add_resource_based_on_original(original.id, clone.id)
            for task_distribution in self.task_resource_distribution
            if task_distribution in original_task_distributions
        ]

        return [
            task_distribution
            for task_distribution in self.task_resource_distribution
            if task_distribution not in original_task_distributions
        ] + new_task_distributions

    def _clone_resource_profiles(self, _: Resource, clone: Resource, assigned_tasks: list[str]):
        """Get a Clone of the Resource Profiles, with the new resource added."""
        original_resource_profiles = [self.get_resource_profile(task) for task in assigned_tasks]

        new_resource_profiles = [
            replace(
                resource_profile,
                resource_list=resource_profile.resource_list + [clone],
            )
            for resource_profile in original_resource_profiles
            if resource_profile is not None
        ]

        return [
            resource_profile
            for resource_profile in self.resource_profiles
            if resource_profile not in original_resource_profiles
        ] + new_resource_profiles

    def batching_rules_debug_str(self) -> str:
        """Get the batching rules as a string."""
        lines = []
        for batching_rule in self.batch_processing:
            lines.append(f"\tTask: {batching_rule.task_id}")
            or_lines = []
            for or_rule in batching_rule.firing_rules:
                and_lines = []
                for rule in or_rule:
                    and_lines.append(f"\t\t{rule.attribute} {rule.comparison} {rule.value}\n")
                or_lines.append("\t\tAND\n".join(and_lines))
            lines.append("\tOR\n".join(or_lines))
        return "\n".join(lines)

    def print_batching_rules(self) -> None:
        """Print the batching rules."""
        info(self.batching_rules_debug_str())

    def is_valid(self) -> bool:
        """Check if the timetable is valid.

        The timetable is valid if all calendars are valid.
        TODO: Add more checks.
        """
        return all(calendar.is_valid() for calendar in self.resource_calendars) and all(
            rule.is_valid() for rule in self.batch_processing
        )

    def __hash__(self) -> int:
        """Hash the timetable.

        NOTE: We cache the hash in a __dict__ field, because we need to
        make sure that the hash is only computed once. functools don't
        work for __hash__.
        """
        if "_hash" in self.__dict__:
            return self.__dict__["_hash"]
        self.__dict__["_hash"] = hash_int(self.to_json())
        return self.__dict__["_hash"]
