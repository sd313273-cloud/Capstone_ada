"""
graph.py - Graph representation and Dijkstra's Shortest Path algorithm.

Implements Dijkstra's algorithm using a min-priority queue (heapq) to compute
shortest travel distances and reconstruct paths between the delivery depot
and drop-off nodes in the courier network.
"""

import heapq
from typing import Dict, List, Optional, Tuple


def dijkstra(graph: Dict[int, Dict[int, int]],
             start_node: int) -> Tuple[Dict[int, int], Dict[int, Optional[int]]]:
    """
    Computes single-source shortest paths from start_node to all reachable nodes.

    Uses a binary min-heap (via Python's heapq) for O((V + E) log V) efficiency.

    Args:
        graph: Adjacency dictionary {node: {neighbor: weight, ...}}.
        start_node: Starting node index.

    Returns:
        Tuple of:
        - distances: Dict mapping each node to the shortest distance from start_node.
        - predecessors: Dict mapping each node to its parent in the shortest-path tree.
    """
    # Initialize distances to infinity and start_node distance to 0
    distances: Dict[int, int] = {node: float("inf") for node in graph}  # type: ignore
    predecessors: Dict[int, Optional[int]] = {node: None for node in graph}
    distances[start_node] = 0

    # Priority queue stores tuples of (distance, node)
    pq: List[Tuple[int, int]] = [(0, start_node)]

    while pq:
        curr_dist, u = heapq.heappop(pq)

        # Skip stale entries in heap (lazy deletion)
        if curr_dist > distances[u]:
            continue

        # Relaxation step for all adjacent edges (u, v) with weight w
        for v, weight in graph[u].items():
            new_dist = curr_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    return distances, predecessors


def reconstruct_path(predecessors: Dict[int, Optional[int]],
                     start_node: int, target_node: int) -> List[int]:
    """
    Reconstructs the node-by-node sequence from start_node to target_node
    by backtracking through the predecessors map.

    Args:
        predecessors: Parent pointers returned by Dijkstra.
        start_node: Origin node.
        target_node: Destination node.

    Returns:
        List of nodes representing the shortest path from start_node to target_node.
    """
    if start_node == target_node:
        return [start_node]

    path: List[int] = []
    curr: Optional[int] = target_node

    while curr is not None:
        path.append(curr)
        if curr == start_node:
            break
        curr = predecessors[curr]

    if not path or path[-1] != start_node:
        # Target is unreachable from start_node
        return []

    path.reverse()
    return path


def compute_all_pairs_for_nodes(graph: Dict[int, Dict[int, int]],
                                nodes_of_interest: List[int]) -> Tuple[Dict[int, Dict[int, int]],
                                                                      Dict[int, Dict[int, List[int]]]]:
    """
    Computes pairwise shortest distances and paths among a specific subset of nodes
    (e.g., depot and chosen parcel destinations).

    Runs Dijkstra rooted at each node of interest.

    Args:
        graph: Adjacency dictionary.
        nodes_of_interest: Unique nodes whose pairwise distances are needed.

    Returns:
        Tuple of:
        - dist_matrix: dist_matrix[u][v] = shortest distance from u to v.
        - path_matrix: path_matrix[u][v] = list of nodes on shortest path from u to v.
    """
    dist_matrix: Dict[int, Dict[int, int]] = {u: {} for u in nodes_of_interest}
    path_matrix: Dict[int, Dict[int, List[int]]] = {u: {} for u in nodes_of_interest}

    unique_nodes = list(dict.fromkeys(nodes_of_interest))

    for source in unique_nodes:
        distances, predecessors = dijkstra(graph, source)
        for target in unique_nodes:
            dist_matrix[source][target] = distances[target]
            path_matrix[source][target] = reconstruct_path(predecessors, source, target)

    return dist_matrix, path_matrix


if __name__ == "__main__":
    # Self-test graph
    test_graph = {
        0: {1: 4, 2: 2},
        1: {0: 4, 2: 1, 3: 5},
        2: {0: 2, 1: 1, 3: 8, 4: 10},
        3: {1: 5, 2: 8, 4: 2},
        4: {2: 10, 3: 2}
    }

    distances, predecessors = dijkstra(test_graph, start_node=0)
    print("Dijkstra distances from depot (0):", distances)
    print("Shortest path 0 -> 4:", reconstruct_path(predecessors, 0, 4))

