from dataclass_wizard import DumpMixin, LoadMixin

from o2.models.timetable.time_period import TimePeriod


class CustomDumper(DumpMixin):
    def __init_subclass__(cls):
        super().__init_subclass__()
        # register dump hooks for custom types - used when `to_dict()` is called
        cls.register_dump_hook(TimePeriod, cls.dump_with_time_period)

    @staticmethod
    def dump_with_time_period(o: TimePeriod, *_):
        return o.model_dump(by_alias=True)


class CustomLoader(LoadMixin):
    def __init_subclass__(cls):
        super().__init_subclass__()
        # register load hooks for custom types - used when `from_dict()` is called
        cls.register_load_hook(TimePeriod, cls.load_to_time_period)

    @staticmethod
    def load_to_time_period(d: str | TimePeriod | dict, base_type: type[TimePeriod]) -> TimePeriod:
        if isinstance(d, base_type):
            return d
        if isinstance(d, str):
            return TimePeriod.model_validate_json(d)

        if isinstance(d, dict):
            return TimePeriod.model_validate(d)

        raise ValueError(f"Can't load {d} to TimePeriod")
