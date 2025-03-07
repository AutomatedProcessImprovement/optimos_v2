import numpy as np
import heapq
import time
from sklearn.neighbors import KDTree
from rtree import index


# Generate random points
def generate_random_points(num_points):
    return np.random.rand(num_points, 2)


# Distance function
def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# Benchmarking function
def benchmark():
    num_iterations = 2500
    initial_points = 5
    points_per_iteration = 10
    pops_per_iteration = 0
    queries_per_iteration = 20
    dimensions = 2

    # Track times
    times_heap = []
    times_kd_tree = []
    times_rtree = []

    # Initial random points
    points = generate_random_points(initial_points)

    # Create the R-tree and k-d tree
    rtree_idx = index.Index()
    kd_tree_points = points.copy()

    # Insert initial points into the R-tree and heap
    for i, point in enumerate(points):
        rtree_idx.insert(i, (*point, *point))

    for iteration in range(num_iterations):
        # Generate new points and choose a random query point
        new_points = generate_random_points(points_per_iteration)
        query_point = np.random.rand(2)

        # Measure time for k-d tree
        start_time = time.time()
        kd_tree_points = np.vstack((kd_tree_points, new_points))
        kd_tree = KDTree(kd_tree_points)
        for _ in range(queries_per_iteration):
            query_point = np.random.rand(2)
            dists, idxs = kd_tree.query([query_point], k=1)

        for _ in range(pops_per_iteration):
            dists, idxs = kd_tree.query([query_point], k=1)
            kd_tree_points = np.delete(kd_tree_points, idxs[0], axis=0)
            kd_tree = KDTree(kd_tree_points)

        times_kd_tree.append(time.time() - start_time)

        # Measure time for R-tree
        start_time = time.time()
        for i, point in enumerate(new_points):
            rtree_idx.insert(i + iteration * points_per_iteration, (*point, *point))

        for _ in range(queries_per_iteration):
            query_point = np.random.rand(2)
            nearest_rtree = next(rtree_idx.nearest((*query_point, *query_point), 1, objects=True))

        for _ in range(pops_per_iteration):
            nearest_rtree = next(rtree_idx.nearest((*query_point, *query_point), 1, objects=True))
            rtree_idx.delete(nearest_rtree.id, nearest_rtree.bbox)

        times_rtree.append(time.time() - start_time)

    # Average times

    avg_time_kd_tree = sum(times_kd_tree) / len(times_kd_tree)
    avg_time_rtree = sum(times_rtree) / len(times_rtree)

    return avg_time_kd_tree, avg_time_rtree


# Run the benchmark
avg_time_kd_tree, avg_time_rtree = benchmark()


print(f"Average time (k-d Tree): {avg_time_kd_tree}")
print(f"Average time (R-tree): {avg_time_rtree}")
