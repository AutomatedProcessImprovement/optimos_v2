
from o2.store import Store
from o2.actions.action_selector import ActionSelector



def test_only_one_rule(store: Store):
    bestAction = ActionSelector.find_most_impactful_batching_rule(store)
    assert bestAction is not None
    assert bestAction.id() == store.state.timetable.batch_processing[0].id()
    

