"""
benchmark.py - Performance Benchmarking and Runtime Analysis.

Measures the execution time of each algorithmic stage:
1. Merge Sort
2. 0/1 Knapsack Dynamic Programming
3. Dijkstra's Shortest Paths
4. Nearest-Neighbor TSP Approximation

Runs across varying problem sizes (10, 50, 100, 200, 500 parcels),
prints formatted comparison tables, and plots runtime scaling curves to 'runtime.png'.
"""

import os
import sys
import time
from typing import Dict, List, Tuple

# Ensure module imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from courier_planner.parcels import (
    load_dataset_from_json,
    generate_dataset,
    create_default_datasets,
    Parcel
)
from courier_planner.sorting import merge_sort
from courier_planner.knapsack import solve_knapsack
from courier_planner.graph import compute_all_pairs_for_nodes
from courier_planner.tsp import nearest_neighbor_tsp


def benchmark_single_instance(parcels: List[Parcel],
                              graph: Dict[int, Dict[int, int]],
                              capacity: int,
                              num_trials: int = 5) -> Dict[str, float]:
    """
    Measures the runtime of each pipeline stage using time.perf_counter().

    Repeats execution across multiple trials to compute a stable average.

    Args:
        parcels: Inventory of parcels.
        graph: Road network adjacency dict.
        capacity: Vehicle weight capacity.
        num_trials: Repetitions for timing stability.

    Returns:
        Dictionary of mean execution times in milliseconds.
    """
    sort_times: List[float] = []
    knap_times: List[float] = []
    dijk_times: List[float] = []
    tsp_times: List[float] = []

    for _ in range(num_trials):
        # 1. Benchmark Merge Sort
        t0 = time.perf_counter()
        sorted_parcels = merge_sort(parcels)
        t1 = time.perf_counter()
        sort_times.append((t1 - t0) * 1000.0)

        # 2. Benchmark 0/1 Knapsack DP
        t0 = time.perf_counter()
        selected_parcels, _, _ = solve_knapsack(sorted_parcels, capacity, print_table=False)
        t1 = time.perf_counter()
        knap_times.append((t1 - t0) * 1000.0)

        # Prepare nodes of interest
        depot = 0
        dest_nodes = sorted(list({p.dest_node for p in selected_parcels}))
        nodes_of_interest = [depot] + [n for n in dest_nodes if n != depot]

        # 3. Benchmark Dijkstra Shortest Paths
        t0 = time.perf_counter()
        dist_matrix, path_matrix = compute_all_pairs_for_nodes(graph, nodes_of_interest)
        t1 = time.perf_counter()
        dijk_times.append((t1 - t0) * 1000.0)

        # 4. Benchmark Nearest-Neighbor TSP
        t0 = time.perf_counter()
        _ = nearest_neighbor_tsp(depot, dest_nodes, dist_matrix, path_matrix)
        t1 = time.perf_counter()
        tsp_times.append((t1 - t0) * 1000.0)

    # Calculate average runtime in ms
    avg = lambda lst: sum(lst) / len(lst)
    return {
        "sort_ms": avg(sort_times),
        "knapsack_ms": avg(knap_times),
        "dijkstra_ms": avg(dijk_times),
        "tsp_ms": avg(tsp_times),
        "total_ms": avg(sort_times) + avg(knap_times) + avg(dijk_times) + avg(tsp_times)
    }


def run_benchmarks(sizes: List[int] = [10, 50, 100, 200, 500]) -> List[dict]:
    """
    Executes benchmark evaluations across predefined parcel inventory sizes.

    Returns:
        List of result dictionaries.
    """
    results = []

    print("\n" + "=" * 90)
    print("                MINI-COURIER PLANNER: ALGORITHM RUNTIME BENCHMARK")
    print("=" * 90)
    print(f"Timing {len(sizes)} problem scales with 5 iterations each using time.perf_counter()...\n")

    for size in sizes:
        # Scale nodes and vehicle capacity proportionally to problem size
        nodes = max(8, size // 5)
        capacity = min(200, max(25, size // 3))

        parcels, graph, cap = generate_dataset(
            num_parcels=size,
            num_nodes=nodes,
            vehicle_capacity=capacity,
            seed=42 + size
        )

        timings = benchmark_single_instance(parcels, graph, cap, num_trials=5)
        timings.update({
            "size": size,
            "nodes": nodes,
            "capacity": cap
        })
        results.append(timings)

    # Print ASCII Comparison Table
    print(f"{'Size (N)':<10}{'Nodes (V)':<11}{'Cap (W)':<10}{'Sort (ms)':<14}{'Knapsack (ms)':<16}{'Dijkstra (ms)':<16}{'TSP (ms)':<12}{'Total (ms)':<12}")
    print("-" * 101)
    for r in results:
        print(f"{r['size']:<10}{r['nodes']:<11}{r['capacity']:<10}"
              f"{r['sort_ms']:<14.4f}{r['knapsack_ms']:<16.4f}"
              f"{r['dijkstra_ms']:<16.4f}{r['tsp_ms']:<12.4f}{r['total_ms']:<12.4f}")
    print("=" * 101 + "\n")

    return results


def run_dataset_benchmarks() -> None:
    """Benchmarks the saved small.json and large.json files."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    small_path = os.path.join(data_dir, "small.json")
    large_path = os.path.join(data_dir, "large.json")

    if not os.path.exists(small_path) or not os.path.exists(large_path):
        create_default_datasets()

    print("\n" + "=" * 80)
    print("           BENCHMARK ON STANDARD DATASETS (data/small & data/large)")
    print("=" * 80)

    for name, path in [("Small Dataset (10 Parcels, 8 Nodes)", small_path),
                       ("Large Dataset (500 Parcels, 100 Nodes)", large_path)]:
        parcels, graph, cap = load_dataset_from_json(path)
        t = benchmark_single_instance(parcels, graph, cap, num_trials=5)
        print(f"\n--- {name} ---")
        print(f"  Parcels: {len(parcels)}, Nodes: {len(graph)}, Capacity: {cap} kg")
        print(f"  Merge Sort:    {t['sort_ms']:8.4f} ms")
        print(f"  0/1 Knapsack:  {t['knapsack_ms']:8.4f} ms")
        print(f"  Dijkstra:      {t['dijkstra_ms']:8.4f} ms")
        print(f"  TSP (NN):      {t['tsp_ms']:8.4f} ms")
        print(f"  Total Runtime: {t['total_ms']:8.4f} ms")
    print("=" * 80 + "\n")


def plot_runtime_chart(results: List[dict], output_paths: List[str]) -> None:
    """
    Generates a high-quality visualization of algorithmic scaling and saves it to PNG.

    Args:
        results: Benchmark records across sizes.
        output_paths: Destination file paths for the saved chart.
    """
    sizes = [r["size"] for r in results]
    sort_ms = [r["sort_ms"] for r in results]
    knap_ms = [r["knapsack_ms"] for r in results]
    dijk_ms = [r["dijkstra_ms"] for r in results]
    tsp_ms = [r["tsp_ms"] for r in results]

    # Create 2-panel figure: Line chart (log-scale) and Stacked Bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.patch.set_facecolor("#FAFAFA")

    # Colors
    c_sort = "#1f77b4"      # Blue
    c_knap = "#ff7f0e"      # Orange
    c_dijk = "#2ca02c"      # Green
    c_tsp = "#d62728"       # Red

    # -------------------------------------------------------------
    # Subplot 1: Algorithm Runtime Curves
    # -------------------------------------------------------------
    ax1.set_facecolor("#FFFFFF")
    ax1.plot(sizes, sort_ms, marker="o", linewidth=2.2, color=c_sort, label="Merge Sort (O(N log N))")
    ax1.plot(sizes, knap_ms, marker="s", linewidth=2.2, color=c_knap, label="0/1 Knapsack DP (O(N * W))")
    ax1.plot(sizes, dijk_ms, marker="^", linewidth=2.2, color=c_dijk, label="Dijkstra Shortest Paths (K * O((V+E)log V))")
    ax1.plot(sizes, tsp_ms, marker="d", linewidth=2.2, color=c_tsp, label="Nearest-Neighbor TSP (O(K^2))")

    ax1.set_title("Algorithm Execution Time vs. Input Size", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Number of Parcels (N)", fontsize=11, fontweight="semibold")
    ax1.set_ylabel("Execution Time (milliseconds)", fontsize=11, fontweight="semibold")
    ax1.set_xticks(sizes)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left", frameon=True, fontsize=10)

    # -------------------------------------------------------------
    # Subplot 2: Stage Proportion Stacked Bar Chart
    # -------------------------------------------------------------
    ax2.set_facecolor("#FFFFFF")
    bar_width = 0.5
    indices = range(len(sizes))

    ax2.bar(indices, sort_ms, width=bar_width, color=c_sort, label="Merge Sort")
    ax2.bar(indices, knap_ms, width=bar_width, bottom=sort_ms, color=c_knap, label="0/1 Knapsack")
    bottom_dijk = [sort_ms[i] + knap_ms[i] for i in range(len(sizes))]
    ax2.bar(indices, dijk_ms, width=bar_width, bottom=bottom_dijk, color=c_dijk, label="Dijkstra")
    bottom_tsp = [bottom_dijk[i] + dijk_ms[i] for i in range(len(sizes))]
    ax2.bar(indices, tsp_ms, width=bar_width, bottom=bottom_tsp, color=c_tsp, label="TSP (NN)")

    ax2.set_title("Total Pipeline Latency Breakdown", fontsize=13, fontweight="bold", pad=12)
    ax2.set_xlabel("Problem Instance Scale (N Parcels)", fontsize=11, fontweight="semibold")
    ax2.set_ylabel("Stacked Execution Time (ms)", fontsize=11, fontweight="semibold")
    ax2.set_xticks(indices)
    ax2.set_xticklabels([f"N={s}" for s in sizes])
    ax2.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax2.legend(loc="upper left", frameon=True, fontsize=10)

    plt.suptitle("Mini-Courier Planner: Empirical Algorithmic Complexity Benchmark",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()

    for path in output_paths:
        plt.savefig(path, dpi=300, bbox_inches="tight")
        print(f"[+] Saved benchmark chart to: {path}")

    plt.close()


def main():
    # 1. Run benchmarks on standard datasets
    run_dataset_benchmarks()

    # 2. Run scaling benchmarks across sizes: 10, 50, 100, 200, 500
    results = run_benchmarks(sizes=[10, 50, 100, 200, 500])

    # 3. Save plot to both courier_planner/runtime.png and ./runtime.png
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(base_dir, ".."))
    chart_paths = [
        os.path.join(base_dir, "runtime.png"),
        os.path.join(workspace_dir, "runtime.png")
    ]
    plot_runtime_chart(results, chart_paths)


if __name__ == "__main__":
    main()

