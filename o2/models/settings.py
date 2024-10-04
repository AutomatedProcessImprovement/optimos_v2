import os
from dataclasses import dataclass

from o2.models.legacy_approach import LegacyApproach


@dataclass()
class Settings:
    """Settings for the Optimos v2 application.

    This class is initialized with sensible defaults, but can be changed to
    suit the needs of the user, e.g. to run it in legacy optimos mode.
    """

    max_non_improving_actions = 1000
    """The maximum number of actions before the application stops."""
    max_iterations = 1000
    """The maximum (total) number of iterations before the application stops."""

    optimos_legacy_mode = False
    """Should this application behave like an approximation of the original OPTIMOS?"""

    only_allow_low_last = True
    """Should `low` rated Actions be tried last?

    E.g. ONLY if no other/higher Action is available.
    """

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    show_simulation_errors = True
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """

    legacy_approach = LegacyApproach.CALENDAR_FIRST
    """
    This Setting is used to simulate different approaches used by legacy optimos.

    While _FIRST / _ONLY are self explanatory, the the _NEXT aka combined mode is a bit more complex.
    The combined mode is a mode where the calendar and resources are optimized at the same time.
    Legacy Optimos will first try calendar and then resources, if the calendar optimization
    finds a result, the resources are still optimized.

    To reproduce this in the new Optimos, we have to do the following:
    - We initialize the setting with calendar first,
    - In this case calendar optimizations will get a higher prio, 
      the resource optimizations will get a "low" prio, that will only(!)
      be executed after the calendar optimization
    - Then as soon as one of the calendar optimizations is successful, 
      we switch this setting to resources first, so that the resources
      are optimized first, and the calendar is optimized afterwards.
    """

    max_threads = os.cpu_count() or 1
    """The maximum number of threads to use for parallel evaluation."""

    max_number_of_actions_to_select = os.cpu_count() or 1
    """The maximum number of actions to select for for (parallel) evaluation."""

    def set_next_combined_mode_status(self) -> None:
        """Set the next combined mode status."""
        self.legacy_approach = self.legacy_approach.next_combined()
