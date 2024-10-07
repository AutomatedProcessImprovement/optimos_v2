import heapq
import random
import numpy as np
from sklearn.neighbors import KDTree
from rtree import index
import time


# Generate random 2D points
def generate_random_points(n):
    return np.random.rand(n, 2)


# Priority queue (heap) implementation for nearest neighbor search
class Heap:
    def __init__(self):
        self.points = []  # Keep points as they were added

    def insert(self, points):
        # Store the points, we will update the heap when a query is made
        self.points.extend(points)

    def update_heap(self, query_point):
        # Rebuild the heap based on the distance to the new query point
        self.heap = []
        for point in self.points:
            distance = np.linalg.norm(point - query_point)
            heapq.heappush(self.heap, (distance, tuple(point)))

    def nearest_neighbor(self):
        # Return the point with the minimum distance
        return heapq.heappop(self.heap)


# Function to benchmark each data structure
def benchmark():
    num_iterations = 100  # Number of insert and search operations
    num_points_per_iteration = 50  # Points to insert each time
    dimensions = 2  # Time and cost (2D)

    # Initialize R-tree, KD-tree and heap structures
    kd_tree_points = np.empty((0, dimensions))
    r_tree_idx = index.Index()
    heap = Heap()

    # Time results
    times_kd_tree = []
    times_r_tree = []
    times_heap = []

    for i in range(num_iterations):
        # Generate 50 random points
        points = generate_random_points(num_points_per_iteration)

        # Random query point for nearest neighbor search
        query_point = generate_random_points(1)[0]

        #### KD Tree ####
        start_time = time.time()
        # Insert points into kd-tree and search for the nearest neighbor
        kd_tree_points = np.vstack([kd_tree_points, points])
        kd_tree = KDTree(kd_tree_points)
        kd_tree.query([query_point], k=1)
        times_kd_tree.append(time.time() - start_time)

        #### R-tree ####
        start_time = time.time()
        # Insert points into R-tree and search for the nearest neighbor
        for idx, point in enumerate(points):
            r_tree_idx.insert(i * num_points_per_iteration + idx, (*point, *point))
        list(r_tree_idx.nearest((*query_point, *query_point), 1))
        times_r_tree.append(time.time() - start_time)

        #### Heap (priority queue) ####
        start_time = time.time()
        # Insert points into the heap
        heap.insert(points)
        # Recalculate the heap based on the new query point
        heap.update_heap(query_point)
        # Find the nearest neighbor
        heap.nearest_neighbor()
        times_heap.append(time.time() - start_time)

    # Output average times
    print(f"KD-Tree average time per iteration: {np.mean(times_kd_tree):.6f} seconds")
    print(f"R-Tree average time per iteration: {np.mean(times_r_tree):.6f} seconds")
    print(f"Heap average time per iteration: {np.mean(times_heap):.6f} seconds")


# Run the benchmark
if __name__ == "__main__":
    benchmark()
