MAX_NON_IMPROVING_ACTIONS = 1000

MAX_ITERATIONS = 1000

OPTIMOS_LEGACY_MODE = False
"""Should this application behave like an approximation of the original OPTIMOS?"""

ONLY_ALLOW_LOW_LAST = True
OPTIMIZE_CALENDAR_FIRST = True
"""This is a setting similar to optimos CA/AR | AR/CA Setting

Should the Calendar be modified first, and then resources added/removed
or vice versa?
"""

PRINT_CHOSEN_ACTIONS = False

SHOW_SIMULATION_ERRORS = False
"""Should the simulation errors be shown?

Most of the time this is not needed, as the errors might just indicate an invalid state,
which will just result in the action not being chosen.
"""
