"""
tsp.py - Traveling Salesperson Problem (TSP) Nearest-Neighbor Approximation.

Finds an efficient delivery tour starting from depot (node 0), visiting all
destinations of selected parcels, and returning to the depot. Uses the Greedy
Nearest-Neighbor heuristic over the shortest-path metric graph computed by Dijkstra.
"""

from typing import Dict, List, Tuple


def nearest_neighbor_tsp(depot: int, delivery_nodes: List[int],
                         dist_matrix: Dict[int, Dict[int, int]],
                         path_matrix: Dict[int, Dict[int, List[int]]]) -> Tuple[List[int], List[int], int]:
    """
    Computes a delivery tour using the Nearest-Neighbor heuristic.

    Algorithm:
    1. Start at depot (node 0).
    2. Among all unvisited delivery destinations, greedily choose the one with
       the smallest shortest-path distance from the current node.
    3. Move to that destination, mark it visited, and append to the tour.
    4. Repeat until all destinations are visited.
    5. Return from the last destination back to the depot.

    Complexity:
        For K delivery stops:
        - Tour construction: O(K^2) comparisons.
        - Approximation ratio: O(log K) for metric TSP; widely used in real-time dispatch.

    Args:
        depot: Index of the central depot (node 0).
        delivery_nodes: List of destination node indices for loaded parcels.
        dist_matrix: Pairwise shortest distances from Dijkstra.
        path_matrix: Pairwise node-by-node shortest paths from Dijkstra.

    Returns:
        Tuple of:
        - tour_stops: Sequence of delivery stops visited [depot, stop_1, ..., depot].
        - full_path: Complete node-by-node path through the road network.
        - total_distance: Total distance units of the closed round-trip tour.
    """
    # Filter out duplicate destinations and exclude depot from unvisited set
    unvisited = set(delivery_nodes)
    unvisited.discard(depot)

    if not unvisited:
        # Trivial case: no parcels or all at depot
        return [depot, depot], [depot], 0

    tour_stops: List[int] = [depot]
    full_path: List[int] = [depot]
    total_distance: int = 0
    current_node = depot

    while unvisited:
        # Find the nearest unvisited delivery location
        # Tie-break by node index for deterministic routing
        next_node = min(
            unvisited,
            key=lambda candidate: (dist_matrix[current_node][candidate], candidate)
        )

        leg_distance = dist_matrix[current_node][next_node]
        total_distance += leg_distance

        # Append intermediate road nodes (excluding the first since it's current_node)
        leg_path = path_matrix[current_node][next_node]
        if len(leg_path) > 1:
            full_path.extend(leg_path[1:])

        tour_stops.append(next_node)
        unvisited.remove(next_node)
        current_node = next_node

    # Return leg: from the last delivery stop back to the depot
    return_dist = dist_matrix[current_node][depot]
    total_distance += return_dist
    return_path = path_matrix[current_node][depot]
    if len(return_path) > 1:
        full_path.extend(return_path[1:])
    tour_stops.append(depot)

    return tour_stops, full_path, total_distance


def print_route_summary(tour_stops: List[int], full_path: List[int],
                        total_distance: int,
                        dist_matrix: Dict[int, Dict[int, int]]) -> None:
    """
    Prints a clear, formatted summary of the courier's delivery route.

    Args:
        tour_stops: Main stops in delivery order.
        full_path: Complete sequence of vertices traversed.
        total_distance: Cumulative travel distance.
        dist_matrix: Pairwise distance matrix for leg details.
    """
    print("\n" + "=" * 70)
    print("COURIER DELIVERY ROUTE PLAN (Nearest-Neighbor TSP)")
    print("=" * 70)

    # 1. Delivery Stops
    stops_display = " -> ".join(
        f"Depot({s})" if s == 0 else f"Node {s}" for s in tour_stops
    )
    print(f"Delivery Stop Sequence ({len(tour_stops) - 1} legs):")
    print(f"  {stops_display}\n")

    # 2. Leg-by-leg breakdown
    print("Leg-by-Leg Details:")
    cum_dist = 0
    for i in range(len(tour_stops) - 1):
        u = tour_stops[i]
        v = tour_stops[i + 1]
        leg_len = dist_matrix[u][v]
        cum_dist += leg_len
        u_label = f"Depot(0)" if u == 0 else f"Node {u}"
        v_label = f"Depot(0)" if v == 0 else f"Node {v}"
        print(f"  Leg {i + 1:2d}: {u_label:<10} --> {v_label:<10} | Distance: {leg_len:3d} km | Cum: {cum_dist:3d} km")

    # 3. Full road network navigation
    print("\nDetailed Road-Network Navigation (All Junctions Traversed):")
    nav_str = " -> ".join(str(n) for n in full_path)
    print(f"  {nav_str}")

    print(f"\nTotal Round-Trip Distance: {total_distance} km")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Self-test with simulated pairwise distances
    sample_depot = 0
    sample_deliveries = [2, 4, 1]

    # Symmetric distance matrix
    sample_dist = {
        0: {0: 0, 1: 10, 2: 15, 4: 20},
        1: {0: 10, 1: 0, 2: 35, 4: 25},
        2: {0: 15, 1: 35, 2: 0, 4: 30},
        4: {0: 20, 1: 25, 2: 30, 4: 0}
    }

    sample_paths = {
        u: {v: [u, v] for v in sample_dist[u]}
        for u in sample_dist
    }

    stops, full, total_dist = nearest_neighbor_tsp(
        sample_depot, sample_deliveries, sample_dist, sample_paths
    )
    print_route_summary(stops, full, total_dist, sample_dist)

