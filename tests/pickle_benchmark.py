import copy
import pickle
import time
import os


def benchmark_pickle(
    store,
    num_objects=10000,
    batch_size=100,
    filename_single="single.pkl",
    filename_batch="batch.pkl",
):
    """Benchmark Pickle performance for single vs. batch dumping."""

    solutions = [
        copy.deepcopy(solution)
        for solution in (
            store.solution_tree.evaluation_discarded_solutions
            + list(store.solution_tree.solution_lookup.values()) * 10
        )
    ]

    print(f"Number of solutions: {len(solutions)}")
    # Ensure old files are removed
    for filename in [filename_single, filename_batch]:
        if os.path.exists(filename):
            os.remove(filename)

    # Single dump (one-by-one)
    with open(filename_single, "wb") as f_single:
        start_time = time.time()
        for i in range(num_objects):
            solution = solutions[i % len(solutions)]
            pickle.dump(solution, f_single, protocol=pickle.HIGHEST_PROTOCOL)
            f_single.flush()
    single_time = time.time() - start_time
    single_size = os.path.getsize(filename_single)

    # Batch dump (every batch_size solutions)
    with open(filename_batch, "wb") as f_batch:
        start_time = time.time()
        buffer = []
        for i in range(num_objects):
            buffer.append(solutions[i % len(solutions)])
            if (i + 1) % batch_size == 0:  # Dump every batch_size elements
                pickle.dump(buffer, f_batch, protocol=pickle.HIGHEST_PROTOCOL)
                buffer = []
        if buffer:  # Dump remaining objects
            pickle.dump(buffer, f_batch, protocol=pickle.HIGHEST_PROTOCOL)
            f_batch.flush()
    batch_time = time.time() - start_time
    batch_size = os.path.getsize(filename_batch)

    # Print results
    print(f"Single dump: {single_time:.4f} sec, File size: {single_size / 1024:_.2f} KB")
    print(f"Batch dump : {batch_time:.4f} sec, File size: {batch_size / 1024:_.2f} KB")


store = pickle.load(
    open(
        "/Users/jannis/Dropbox/Uni/Master/BP-Optimization/optimos_v2/stores/store_TABU_SEARCH_2025-01-30_01-07-04.pkl",
        "rb",
    )
)

benchmark_pickle(store)
