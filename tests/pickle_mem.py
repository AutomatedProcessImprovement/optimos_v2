import gc
import pickle
import sys

from guppy import hpy
from pympler import asizeof

hp = hpy()
hp.setrelheap()


with open(sys.argv[1], "rb") as f:
    gc.disable()
    data = pickle.load(f)

print("Loaded data")
# gc.enable()
# print("Enabled gc")
h = hp.heap()

print(h)
# print(asizeof.asized(data, detail=1).format())


"""
Whole Store: size=2682072408 -> 2.68GB
Solution_Tree: size=2673942840 -> 2.67GB

One (Current) Solution: size=1306536 -> 1.31MB
-> around 2000 Solutions -> 2.62GB

State = 636560
    -> 104080 BPMN
    -> 550000 Timetable
Evaluation = 663272
    -> 335000 avg_fixed_cost_per_case_by_task 

Solution(evaluation=Evaluation(hourly_....07:00:00), 'duration_fn': '1/size'})]) size=1306584 flat=48
    __dict__ size=1306536 flat=104
        [V] evaluation: Evaluation(hourly_rates={'End': 20, 'I....AY.WEDNESDAY: 'WEDNESDAY'>: {13: 1}}}) size=663272 flat=48
            __dict__ size=663224 flat=1176
            __class__ size=0 flat=0
        [V] state: State(bpmn_definition='<?xml version=".... total_cases=1000), for_testing=False) size=636560 flat=48
            __dict__ size=636512 flat=104
            __class__ size=0 flat=0
        [V] actions: [AddSizeRuleAction(params={'task_id': ....,07:00:00), 'duration_fn': '1/size'})] size=5616 flat=120
            AddDateTimeRuleByEnablementAction(para....Y,22:00:00), 'duration_fn': '1/size'}) size=1360 flat=48
            AddDateTimeRuleByAvailabilityAction(pa....Y,17:00:00), 'duration_fn': '1/size'}) size=1360 flat=48
            AddDateTimeRuleByEnablementAction(para....Y,07:00:00), 'duration_fn': '1/size'}) size=1360 flat=48
            AddSizeRuleAction(params={'task_id': '...., 'size': 1, 'duration_fn': '1/size'}) size=736 flat=48
            AddSizeRuleAction(params={'task_id': '...., 'size': 1, 'duration_fn': '1/size'}) size=680 flat=48
        [V] parent_state: State(bpmn_definition='<?xml version=".... total_cases=1000), for_testing=False) size=712 flat=48
            __dict__ size=664 flat=104
            __class__ size=0 flat=0
        [K] evaluation size=64 flat=64
        [K] parent_state size=64 flat=64
        [K] state size=56 flat=56
        [K] actions size=56 flat=56
        [V] id: 3248387428 size=32 flat=32
        [K] id size=0 flat=0
    __class__ size=0 flat=0





"""
