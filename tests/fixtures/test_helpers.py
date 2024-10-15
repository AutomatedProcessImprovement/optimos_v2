from dataclasses import replace

from o2.models.solution import Solution
from o2.store import Store


def replace_state(store: Store, **kwargs):
    """Updates the state of the store. (not in place)"""
    new_state = replace(store.solution.state, **kwargs)
    evaluation = new_state.evaluate()
    new_solution = Solution(
        evaluation=evaluation, state=new_state, parent_state=None, actions=[]
    )
    return Store(
        solution=new_solution,
        constraints=store.constraints,
    )


def replace_timetable(store: Store, **kwargs):
    """Updates the timetable of the store. (not in place)"""
    new_timetable = replace(store.solution.state.timetable, **kwargs)
    return replace_state(store, timetable=new_timetable)


def replace_constraints(store: Store, **kwargs):
    """Updates the constraints of the store (not in place)"""
    new_constraints = replace(store.constraints, **kwargs)
    return Store(
        solution=store.solution,
        constraints=new_constraints,
    )
