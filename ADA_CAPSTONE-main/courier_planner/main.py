"""
main.py - End-to-End Pipeline for the Mini-Courier Planner Capstone.

Execution Pipeline:
1. Load dataset (data/small.json or data/large.json).
2. Sort parcels by deadline (ascending) and priority (descending) using custom Merge Sort.
3. Select optimal cargo load within vehicle weight capacity using 0/1 Knapsack DP.
   (Prints DP table for small input).
4. Compute shortest paths using Dijkstra's algorithm.
5. Solve delivery route using Nearest-Neighbor TSP approximation.
6. Print comprehensive results, route sequences, and delivery manifest.
"""

import argparse
import os
import sys

# Ensure module imports work whether executed from root or inside package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from courier_planner.parcels import load_dataset_from_json, create_default_datasets
from courier_planner.sorting import merge_sort
from courier_planner.knapsack import solve_knapsack
from courier_planner.graph import compute_all_pairs_for_nodes
from courier_planner.tsp import nearest_neighbor_tsp, print_route_summary


def run_pipeline(dataset_path: str, force_print_table: bool = False) -> None:
    """
    Executes the complete courier planning workflow.

    Args:
        dataset_path: Path to dataset JSON file.
        force_print_table: If True, forces printing of the DP table.
    """
    print("\n" + "#" * 75)
    print("       MINI-COURIER PLANNER: DAA CAPSTONE OPTIMIZATION PIPELINE")
    print("#" * 75)

    if not os.path.exists(dataset_path):
        print(f"[!] Dataset not found at '{dataset_path}'. Generating default datasets...")
        create_default_datasets()

    print(f"\n[+] Loading problem instance from: {dataset_path}")
    parcels, graph, capacity = load_dataset_from_json(dataset_path)

    print(f"    - Total Parcels Available: {len(parcels)}")
    print(f"    - Network Nodes (Junctions): {len(graph)} (Depot = Node 0)")
    print(f"    - Delivery Vehicle Capacity: {capacity} kg")

    # =========================================================================
    # STAGE 1: SORTING (Divide and Conquer - Merge Sort)
    # =========================================================================
    print("\n" + "=" * 75)
    print("STAGE 1: MERGE SORT (Deadline Ascending, Priority Descending)")
    print("=" * 75)
    print("Sorting parcel inventory without built-in sort()...")

    sorted_parcels = merge_sort(parcels)

    display_count = min(12, len(sorted_parcels))
    print(f"\nTop {display_count} Sorted Parcels (Primary: Deadline, Secondary: Priority):")
    print(f"{'Rank':<6}{'ID':<8}{'Deadline':<12}{'Priority':<12}{'Weight (kg)':<14}{'Destination Node'}")
    print("-" * 65)
    for rank, p in enumerate(sorted_parcels[:display_count], start=1):
        print(f"{rank:<6}P#{p.id:<6}{p.deadline:<12}{p.value:<12}{p.weight:<14}Node {p.dest_node}")

    if len(sorted_parcels) > display_count:
        print(f"... and {len(sorted_parcels) - display_count} more parcels.")

    # =========================================================================
    # STAGE 2: 0/1 KNAPSACK DYNAMIC PROGRAMMING
    # =========================================================================
    print("\n" + "=" * 75)
    print("STAGE 2: 0/1 KNAPSACK SELECTION (Dynamic Programming)")
    print("=" * 75)
    print(f"Selecting maximum-value parcel subset within vehicle capacity W = {capacity} kg...")

    # Print DP table if small instance (N <= 15 and W <= 35) or if explicitly requested
    is_small_instance = (len(sorted_parcels) <= 15 and capacity <= 35)
    should_print_table = force_print_table or is_small_instance

    selected_parcels, total_value, total_weight = solve_knapsack(
        sorted_parcels, capacity, print_table=should_print_table
    )

    print(f"\n[Knapsack Optimization Result]")
    print(f"  - Parcels Accepted for Loading: {len(selected_parcels)} of {len(sorted_parcels)}")
    print(f"  - Total Priority Value:          {total_value} pts")
    print(f"  - Total Weight Utilized:         {total_weight} / {capacity} kg ({total_weight/capacity*100:.1f}%)")
    print(f"  - Remaining Vehicle Capacity:    {capacity - total_weight} kg")

    print("\nLoaded Cargo Manifest:")
    print(f"{'ID':<8}{'Weight':<10}{'Priority':<12}{'Deadline':<12}{'Destination Node'}")
    print("-" * 55)
    for p in selected_parcels:
        print(f"P#{p.id:<6}{p.weight:<10}{p.value:<12}{p.deadline:<12}Node {p.dest_node}")

    # =========================================================================
    # STAGE 3: SHORTEST PATHS (Dijkstra) & ROUTE OPTIMIZATION (TSP Heuristic)
    # =========================================================================
    print("\n" + "=" * 75)
    print("STAGE 3: ROUTING (Dijkstra Shortest Paths + Nearest-Neighbor TSP)")
    print("=" * 75)

    depot = 0
    # Unique destination nodes among the selected parcels
    dest_nodes = sorted(list({p.dest_node for p in selected_parcels}))
    nodes_of_interest = [depot] + [node for node in dest_nodes if node != depot]

    print(f"Key Delivery Stops: Depot (0) + {len(dest_nodes)} distinct destination nodes: {dest_nodes}")
    print(f"Running Dijkstra from {len(nodes_of_interest)} source nodes to compute all-pairs shortest paths...")

    dist_matrix, path_matrix = compute_all_pairs_for_nodes(graph, nodes_of_interest)

    print(f"Solving tour with Nearest-Neighbor TSP approximation...")
    tour_stops, full_path, total_distance = nearest_neighbor_tsp(
        depot, dest_nodes, dist_matrix, path_matrix
    )

    print_route_summary(tour_stops, full_path, total_distance, dist_matrix)

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("#" * 75)
    print("                       FINAL DISPATCH SUMMARY")
    print("#" * 75)
    print(f"Status:            READY FOR DISPATCH")
    print(f"Parcels Delivered: {len(selected_parcels)}")
    print(f"Vehicle Weight:    {total_weight} / {capacity} kg")
    print(f"Priority Yield:    {total_value} points")
    print(f"Delivery Stops:    {len(tour_stops) - 2} intermediate locations + Depot")
    print(f"Total Tour Dist:   {total_distance} km")
    print("#" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Mini-Courier Planner: Algorithms Capstone Pipeline"
    )
    parser.add_argument(
        "--dataset", "-d",
        type=str,
        default="small",
        choices=["small", "large"],
        help="Dataset size to run: 'small' (10 parcels, 8 nodes) or 'large' (500 parcels, 100 nodes)."
    )
    parser.add_argument(
        "--table", "-t",
        action="store_true",
        help="Force printing of the 0/1 Knapsack DP table."
    )
    args = parser.parse_args()

    # Determine file path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_filename = f"{args.dataset}.json"
    dataset_path = os.path.join(script_dir, "data", data_filename)

    run_pipeline(dataset_path, force_print_table=args.table)


if __name__ == "__main__":
    main()

