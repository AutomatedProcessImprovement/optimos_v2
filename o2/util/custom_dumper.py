from typing import Union

from dataclass_wizard import DumpMixin, LoadMixin

from o2.models.timetable.time_period import TimePeriod


class CustomDumper(DumpMixin):
    """Handles custom serialization of complex data types to dictionaries.

    Provides specialized methods for converting complex objects like TimePeriod
    into dictionary representations suitable for serialization.
    """

    def __init_subclass__(cls) -> None:
        """Initialize a subclass with custom dump hooks.

        Registers custom dump hooks for complex types that require special handling.
        """
        super().__init_subclass__()
        # register dump hooks for custom types - used when `to_dict()` is called
        cls.register_dump_hook(TimePeriod, cls.dump_with_time_period)

    @staticmethod
    def dump_with_time_period(o: TimePeriod, *_: object) -> dict:
        """Convert a TimePeriod object to a dictionary.

        Handles the serialization of TimePeriod objects using their model_dump method.
        """
        return o.model_dump(by_alias=True)


class CustomLoader(LoadMixin):
    """Handles custom deserialization from dictionaries to complex data types.

    Provides specialized methods for converting dictionary representations
    back into complex objects like TimePeriod.
    """

    def __init_subclass__(cls) -> None:
        """Initialize a subclass with custom load hooks.

        Registers custom load hooks for complex types that require special handling.
        """
        super().__init_subclass__()
        # register load hooks for custom types - used when `from_dict()` is called
        cls.register_load_hook(TimePeriod, cls.load_to_time_period)

    @staticmethod
    def load_to_time_period(d: Union[str, TimePeriod, dict], base_type: type[TimePeriod]) -> TimePeriod:
        """Convert a dictionary, string, or TimePeriod to a TimePeriod object.

        Handles deserialization of TimePeriod objects from various input formats.
        """
        if isinstance(d, base_type):
            return d
        if isinstance(d, str):
            return TimePeriod.model_validate_json(d)

        if isinstance(d, dict):
            return TimePeriod.model_validate(d)

        raise ValueError(f"Can't load {d} to TimePeriod")
