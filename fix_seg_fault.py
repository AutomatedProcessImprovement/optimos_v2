import os
import pickle
import random

from o2.pareto_front import ParetoFront
import rtree

from o2.store import Store
from tests.fixtures.test_helpers import create_mock_solution

if __name__ == "__main__":
    folder = "/var/folders/dc/mhx8033j757bdr6m2lhpg5h00000gn/T/tmp.YpjCW1z8MX"
    # folder = "stores/run_2025-03-09-01-19-09-609087/"

    store_name = "store_simulated_annealing_bpi_challenge_2012_mid.pkl"

    with open(os.path.join(folder, store_name), "rb") as f:
        store: Store = pickle.load(f)

    print("Loaded store")
    print("Resetting rtree")

    index = rtree.index.Index()

    store.solution_tree.rtree = index

    i = 0
    for solution_id in store.solution_tree.solution_lookup:
        if store.solution_tree.solution_lookup[solution_id] is not None:
            i += 1
            solution = store.solution_tree.solution_lookup[solution_id]
            assert solution is not None
            store.solution_tree.add_solution(solution, archive=False)
            store.solution_tree.add_solution(solution, archive=False)
            if i % 250 == 0:
                print(f"Added the {i}th solution")

    print("Reinserted all solutions")

    bounding_rect = store.current_pareto_front.get_bounding_rect()

    temp = 488.51

    i = 0
    while True:
        i += 1

        solutions = store.solution_tree.get_solutions_near_to_pareto_front(
            store.current_pareto_front, max_distance=temp * random.random()
        )

        solutions2 = store.solution_tree.get_solutions_near_to_pareto_front(
            store.current_pareto_front, max_distance=temp * 1000 * random.random()
        )

        five_random_points_in_bounding_rect = [
            create_mock_solution(
                store.current_state,
                int(random.uniform(bounding_rect[0], bounding_rect[2])),
                int(random.uniform(bounding_rect[1], bounding_rect[3])),
            )
            for _ in range(5)
        ]

        pareto_front = ParetoFront()
        pareto_front.solutions = five_random_points_in_bounding_rect
        nearest = store.solution_tree.get_nearest_solution(pareto_front, max_distance=temp * random.random())
        if i % 100 == 0:
            print(
                f"Ran for the {i}th time (getting {len(solutions) + len(solutions2)} solutions near to pareto front)"
            )
            print(f"\t>Nearest solution is {nearest.id if nearest is not None else 'None'}")
