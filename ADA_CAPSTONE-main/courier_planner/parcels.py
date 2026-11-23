"""
parcels.py - Data structures and dataset generator for Mini-Courier Planner.

Defines the Parcel dataclass, graph generation utilities, and functions
to load/save problem instances to JSON format.
"""

from dataclasses import dataclass, asdict
import json
import random
from typing import Dict, List, Tuple


@dataclass
class Parcel:
    """
    Represents a package to be delivered.

    Attributes:
        id: Unique identifier for the parcel.
        weight: Weight in kilograms (cost against vehicle capacity).
        value: Priority score (higher value = higher importance).
        deadline: Delivery time-window/deadline slot (lower = more urgent).
        dest_node: Destination graph node index (where package must be dropped).
    """
    id: int
    weight: int
    value: int       # Priority
    deadline: int    # Urgency (1 = earliest)
    dest_node: int   # Target delivery node in graph (0 is depot)

    def to_dict(self) -> dict:
        """Convert Parcel instance to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Parcel":
        """Instantiate Parcel from a dictionary."""
        return cls(
            id=int(data["id"]),
            weight=int(data["weight"]),
            value=int(data["value"]),
            deadline=int(data["deadline"]),
            dest_node=int(data["dest_node"])
        )


def generate_connected_graph(num_nodes: int, extra_edge_factor: float = 0.25,
                             min_weight: int = 2, max_weight: int = 25,
                             seed: int = 42) -> Dict[int, Dict[int, int]]:
    """
    Generates a random connected undirected graph with positive integer edge weights.

    To guarantee connectivity, a spanning tree is formed first, followed by
    randomly added cross-edges to simulate a realistic road network.

    Args:
        num_nodes: Total number of nodes (0 = depot, 1..N-1 = delivery locations).
        extra_edge_factor: Fraction of additional random edges beyond spanning tree.
        min_weight: Minimum travel distance/weight between adjacent nodes.
        max_weight: Maximum travel distance/weight between adjacent nodes.
        seed: Random seed for reproducibility.

    Returns:
        Adjacency dictionary mapping node -> {neighbor_node: edge_weight}.
    """
    rng = random.Random(seed)
    adj: Dict[int, Dict[int, int]] = {i: {} for i in range(num_nodes)}

    # Step 1: Guarantee connectivity using a randomized spanning tree
    nodes = list(range(num_nodes))
    connected = [nodes[0]]
    unconnected = nodes[1:]
    rng.shuffle(unconnected)

    for target in unconnected:
        source = rng.choice(connected)
        weight = rng.randint(min_weight, max_weight)
        adj[source][target] = weight
        adj[target][source] = weight
        connected.append(target)

    # Step 2: Add extra edges to create realistic road density and alternative routes
    max_possible_extra = (num_nodes * (num_nodes - 1)) // 2 - (num_nodes - 1)
    extra_edges_count = int(max_possible_extra * extra_edge_factor)

    attempts = 0
    added = 0
    while added < extra_edges_count and attempts < extra_edges_count * 5:
        attempts += 1
        u = rng.randint(0, num_nodes - 1)
        v = rng.randint(0, num_nodes - 1)
        if u != v and v not in adj[u]:
            weight = rng.randint(min_weight, max_weight)
            adj[u][v] = weight
            adj[v][u] = weight
            added += 1

    return adj


def generate_dataset(num_parcels: int, num_nodes: int, vehicle_capacity: int,
                     seed: int = 42) -> Tuple[List[Parcel], Dict[int, Dict[int, int]], int]:
    """
    Generates reproducible parcel orders and a connected road network graph.

    Args:
        num_parcels: Number of parcels to generate.
        num_nodes: Number of locations in the delivery network (node 0 = depot).
        vehicle_capacity: Maximum weight capacity of courier vehicle.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (parcels list, graph adjacency dict, vehicle capacity).
    """
    rng = random.Random(seed)
    graph = generate_connected_graph(num_nodes=num_nodes, seed=seed)

    parcels: List[Parcel] = []
    for i in range(1, num_parcels + 1):
        # Weight between 1 and 10 kg
        weight = rng.randint(1, 10)
        # Priority / value between 5 and 50 points
        value = rng.randint(5, 50)
        # Delivery deadline between time slot 1 and 10
        deadline = rng.randint(1, 10)
        # Destination: any delivery node except depot 0
        dest_node = rng.randint(1, num_nodes - 1)

        parcels.append(Parcel(
            id=i,
            weight=weight,
            value=value,
            deadline=deadline,
            dest_node=dest_node
        ))

    return parcels, graph, vehicle_capacity


def save_dataset_to_json(filepath: str, parcels: List[Parcel],
                         graph: Dict[int, Dict[int, int]],
                         vehicle_capacity: int) -> None:
    """Saves a dataset to a JSON file."""
    # Convert integer keys in graph to strings for standard JSON serialization
    serialized_graph = {
        str(u): {str(v): w for v, w in neighbors.items()}
        for u, neighbors in graph.items()
    }

    data = {
        "vehicle_capacity": vehicle_capacity,
        "parcels": [p.to_dict() for p in parcels],
        "graph": serialized_graph
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_dataset_from_json(filepath: str) -> Tuple[List[Parcel], Dict[int, Dict[int, int]], int]:
    """
    Loads parcels, graph, and vehicle capacity from a JSON file.

    Returns:
        Tuple of (parcels list, graph adjacency dict with integer keys, vehicle capacity).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    capacity = int(data["vehicle_capacity"])
    parcels = [Parcel.from_dict(item) for item in data["parcels"]]

    # Convert graph keys back to integers
    graph: Dict[int, Dict[int, int]] = {}
    for u_str, neighbors in data["graph"].items():
        u = int(u_str)
        graph[u] = {int(v_str): int(w) for v_str, w in neighbors.items()}

    return parcels, graph, capacity


def create_default_datasets():
    """Generates and saves the small (10/8) and large (500/100) datasets."""
    import os

    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Small dataset: 10 parcels, 8 nodes, vehicle capacity = 25
    small_parcels, small_graph, small_cap = generate_dataset(
        num_parcels=10,
        num_nodes=8,
        vehicle_capacity=25,
        seed=42
    )
    save_dataset_to_json(
        os.path.join(data_dir, "small.json"),
        small_parcels,
        small_graph,
        small_cap
    )
    print(f"Generated data/small.json: {len(small_parcels)} parcels, {len(small_graph)} nodes, W={small_cap}")

    # 2. Large dataset: 500 parcels, 100 nodes, vehicle capacity = 150
    large_parcels, large_graph, large_cap = generate_dataset(
        num_parcels=500,
        num_nodes=100,
        vehicle_capacity=150,
        seed=42
    )
    save_dataset_to_json(
        os.path.join(data_dir, "large.json"),
        large_parcels,
        large_graph,
        large_cap
    )
    print(f"Generated data/large.json: {len(large_parcels)} parcels, {len(large_graph)} nodes, W={large_cap}")


if __name__ == "__main__":
    create_default_datasets()

