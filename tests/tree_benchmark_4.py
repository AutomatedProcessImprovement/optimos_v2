import numpy as np
import time
from sklearn.neighbors import KDTree
from rtree import index


# Generate random points
def generate_random_points(num_points):
    return np.random.rand(num_points, 2)


# Generate maxima points that dominate all others
def generate_maxima_points(num_maxima, points):
    # Ensure that maxima are greater than all points in the dataset along both dimensions
    max_coords = np.max(points, axis=0)
    return max_coords + np.random.rand(num_maxima, 2)


# Distance function
def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# Heap operations
class Heap:
    def __init__(self, points):
        self.points = points

    def find_nearest(self, query_point):
        min_dist = float("inf")
        nearest_point = None
        for point in self.points:
            distance = euclidean_distance(point, query_point)
            if distance < min_dist:
                min_dist = distance
                nearest_point = point
        return nearest_point, min_dist


# Benchmarking function
def benchmark():
    num_data_points = 1000
    num_maxima_points = 20

    # Track times
    times_heap = []
    times_kd_tree = []
    times_rtree = []

    # Generate the random dataset
    data_points = generate_random_points(num_data_points)

    # Generate maxima points that dominate the dataset
    maxima_points = generate_maxima_points(num_maxima_points, data_points)

    # Create the R-tree, k-d tree, and heap
    rtree_idx = index.Index()
    kd_tree = KDTree(data_points)
    heap = Heap(data_points)

    # Insert data points into the R-tree
    for i, point in enumerate(data_points):
        rtree_idx.insert(i, (*point, *point))

    for query_point in maxima_points:
        # Measure time for heap
        start_time = time.time()
        nearest_heap, dist_heap = heap.find_nearest(query_point)
        times_heap.append(time.time() - start_time)

        # Measure time for k-d tree
        start_time = time.time()
        _, kd_idx = kd_tree.query([query_point], k=1)
        nearest_kd_tree = kd_tree.data[kd_idx[0][0]]
        times_kd_tree.append(time.time() - start_time)

        # Measure time for R-tree
        start_time = time.time()
        nearest_rtree = list(rtree_idx.nearest((*query_point, *query_point), 1))[0]
        times_rtree.append(time.time() - start_time)

    # Average times
    avg_time_heap = sum(times_heap)
    avg_time_kd_tree = sum(times_kd_tree)
    avg_time_rtree = sum(times_rtree)

    return avg_time_heap, avg_time_kd_tree, avg_time_rtree


# Run the benchmark
avg_time_heap, avg_time_kd_tree, avg_time_rtree = benchmark()

print(f"Average time (Heap): {avg_time_heap}")
print(f"Average time (k-d Tree): {avg_time_kd_tree}")
print(f"Average time (R-tree): {avg_time_rtree}")
