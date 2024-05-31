from dataclasses import dataclass
from typing import List, TypedDict, Union
from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class GlobalConstraints(JSONWizard):
    max_weekly_cap: float
    max_daily_cap: float
    max_consecutive_cap: float
    max_shifts_day: int
    max_shifts_week: float
    is_human: bool


@dataclass(frozen=True)
class DailyStartTimes(JSONWizard):
    monday: Union[int, str]
    tuesday: Union[int, str]
    wednesday: Union[int, str]
    thursday: Union[int, str]
    friday: Union[None, int, str]
    saturday: Union[None, int, str]
    sunday: Union[None, int, str]


@dataclass(frozen=True)
class Constraints(JSONWizard):
    global_constraints: GlobalConstraints
    daily_start_times: DailyStartTimes
    never_work_masks: DailyStartTimes
    always_work_masks: DailyStartTimes


@dataclass(frozen=True)
class ConstraintsResourcesItem(JSONWizard):
    id: str
    constraints: Constraints


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    pass
    # time_var: int
    # max_cap: int
    # max_shift_size: int
    # max_shift_blocks: int
    # hours_in_day: int
    # resources: List[ConstraintsResourcesItem]
