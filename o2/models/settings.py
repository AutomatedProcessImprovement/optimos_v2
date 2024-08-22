from dataclasses import dataclass


@dataclass(frozen=True)
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
    optimize_calendar_first = True
    """This is a setting similar to optimos CA/AR | AR/CA Setting

    Should the Calendar be modified first, and then resources added/removed
    or vice versa?
    """

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    show_simulation_errors = False
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """
