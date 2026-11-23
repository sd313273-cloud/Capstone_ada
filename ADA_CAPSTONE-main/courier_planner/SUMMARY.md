# Project Executive Summary: Mini-Courier Planner

**Course / Subject:** Design and Analysis of Algorithms (DAA Capstone)  
**Project Title:** Mini-Courier Planner  
**Date:** November 2026  

---

## 1. Project Overview & Problem Statement

Last-mile delivery is a critical operational bottleneck in modern supply chains, representing over 40% of overall transportation costs. The **Mini-Courier Planner** models and solves this challenge by integrating four foundational Design and Analysis of Algorithms (DAA) paradigms into an automated, end-to-end dispatch and routing engine:

1. **Order Prioritization:** Ranking pending parcel orders by time urgency and business importance.
2. **Payload Selection:** Selecting the highest-value subset of parcels that satisfies the delivery vehicle's strict weight capacity.
3. **Shortest-Path Traversal:** Computing shortest transit distances across an underlying street junction network.
4. **Tour Optimization:** Synthesizing an efficient round-trip delivery tour that starts and terminates at the central depot.

---

## 2. End-to-End Pipeline Architecture

```
                  [ Raw Parcel Orders & Road Graph ]
                    (data/small.json, data/large.json)
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ STAGE 1: Custom Merge Sort (sorting.py)                │
      │ - Divide-and-Conquer paradigm                         │
      │ - Primary Key: Deadline (ascending)                   │
      │ - Secondary Key: Priority/Value (descending)           │
      │ - Time: Θ(N log N) | Space: O(N)                       │
      │ - Strictly no Python built-in sort()                   │
      └───────────────────────────┬────────────────────────────┘
                                  │ Sorted Inventory
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ STAGE 2: 0/1 Knapsack DP (knapsack.py)                 │
      │ - Dynamic Programming paradigm                         │
      │ - Vehicle Weight Capacity Constraint W                 │
      │ - Formatted 2D DP Table visualization                  │
      │ - Backtracking for optimal item subset recovery        │
      │ - Time: O(N · W) | Space: O(N · W)                     │
      └───────────────────────────┬────────────────────────────┘
                                  │ Selected High-Value Cargo
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ STAGE 3: Dijkstra Shortest Path (graph.py)             │
      │ - Greedy with Binary Min-Heap (heapq)                  │
      │ - Predecessor tracking for junction-level paths        │
      │ - All-pairs metric distance matrix for needed stops    │
      │ - Time: O(K · (V + E) log V) | Space: O(V)             │
      └───────────────────────────┬────────────────────────────┘
                                  │ Metric Graph Distance & Path Matrices
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ STAGE 4: Nearest-Neighbor TSP (tsp.py)                 │
      │ - Heuristic Approximation paradigm                     │
      │ - Round-trip delivery tour starting/ending at Depot 0  │
      │ - Reconstructs full road-network junction navigation   │
      │ - Time: O(K^2) | Space: O(K)                           │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
            [ Final Dispatch Manifest & Road Navigation Plan ]
```

---

## 3. Algorithmic Modules & Complexity Analysis

| Module | Core Algorithm | Paradigm | Time Complexity | Space Complexity | Key Responsibility & Design Choice |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **`sorting.py`** | Merge Sort | Divide & Conquer | $\Theta(N \log N)$ | $O(N)$ | Multi-key ordering without built-in `sort()`. Guarantees stability and eliminates QuickSort's $O(N^2)$ worst-case pivot breakdown. |
| **`knapsack.py`** | 0/1 Knapsack | Dynamic Programming | $O(N \cdot W)$ | $O(N \cdot W)$ | Optimal parcel payload selection within vehicle capacity $W$. Features full DP table printout and backward state recovery. |
| **`graph.py`** | Dijkstra's Algorithm | Greedy (Min-Heap) | $O((V + E) \log V)$ | $O(V)$ | Point-to-point road routing with predecessor backtracking to extract intermediate street junctions. |
| **`tsp.py`** | Nearest-Neighbor TSP | Greedy Heuristic | $O(K^2)$ | $O(K)$ | Fast tour synthesis across $K$ delivery locations, returning to depot. Approximation factor bounded by $O(\log K)$. |
| **`benchmark.py`**| Multi-scale Timer | Empirical Analysis | Multi-trial | $O(1)$ | Precise `time.perf_counter()` benchmarking across sizes 10–500 and chart rendering via `matplotlib`. |

---

## 4. Key Implementation Details

### Module 1: `parcels.py` (Data Structures & Graph Generator)
- **`Parcel` Dataclass:** Attributes: `id`, `weight` (kg), `value` (priority points), `deadline` (urgency slot), `dest_node` (delivery location).
- **Connected Graph Generator:** Builds a guaranteed connected road graph by first creating a randomized spanning tree, then adding extra cross-edges to simulate realistic road density.
- **Reproducible Datasets:**
  - `data/small.json`: 10 parcels, 8 nodes, vehicle capacity $W = 25$ kg.
  - `data/large.json`: 500 parcels, 100 nodes, vehicle capacity $W = 150$ kg.

### Module 2: `sorting.py` (Pure Merge Sort)
- **Zero Built-ins:** Written entirely from scratch.
- **Predicate:**
  $$\text{IsBefore}(A, B) \iff (d_A < d_B) \lor (d_A = d_B \land v_A > v_B) \lor (d_A = d_B \land v_A = v_B \land \text{id}_A < \text{id}_B)$$

### Module 3: `knapsack.py` (0/1 Knapsack DP)
- **Recurrence:**
  $$DP[i][w] = \max(DP[i-1][w], \, DP[i-1][w - w_i] + v_i) \quad \text{for } w \ge w_i$$
- **Visual DP Table:** Renders a formatted ASCII grid with parcels as rows and capacities $0 \dots W$ as columns.
- **Backtracking:** Recovers the exact subset of parcels from state differences $DP[i][w] \ne DP[i-1][w]$.

### Module 4: `graph.py` & `tsp.py` (Routing)
- **Dijkstra:** Min-priority queue using Python's `heapq`. Records parent pointers $\pi[v]$ to reconstruct the exact path between any pair of nodes.
- **TSP Approximation:** Nearest-Neighbor selection over the metric distance matrix; stitches together consecutive shortest paths into a single continuous street traversal.

---

## 5. Experimental Benchmark Results

Timed using high-precision `time.perf_counter()` with 5 iterations per configuration:

### Scaling Across Input Sizes ($N$ Parcels)
| Size ($N$) | Nodes ($V$) | Vehicle Cap ($W$) | Merge Sort (ms) | 0/1 Knapsack (ms) | Dijkstra (ms) | TSP NN (ms) | Total Pipeline (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 8 | 25 kg | 0.0255 ms | 0.0645 ms | 0.0834 ms | 0.0097 ms | **0.1831 ms** |
| **50** | 10 | 25 kg | 0.1278 ms | 0.2907 ms | 0.1938 ms | 0.0194 ms | **0.6318 ms** |
| **100** | 20 | 33 kg | 0.2924 ms | 0.8957 ms | 0.8739 ms | 0.0430 ms | **2.1050 ms** |
| **200** | 40 | 66 kg | 0.8432 ms | 3.1165 ms | 4.7645 ms | 0.1820 ms | **8.9062 ms** |
| **500** | 100 | 166 kg | 1.9565 ms | 22.9689 ms | 41.5610 ms | 0.6082 ms | **67.0946 ms** |

### Standard Pre-Generated Datasets
- **`small.json` (10 parcels, 8 nodes, $W=25$ kg):**
  - Parcels Accepted: **7 of 10** | Capacity Used: **25 / 25 kg (100%)**
  - Priority Score: **129 points** | Tour Distance: **122 km** (6 stops)
  - Total Runtime: **0.277 ms**
- **`large.json` (500 parcels, 100 nodes, $W=150$ kg):**
  - Parcels Accepted: **85 of 500** | Capacity Used: **150 / 150 kg (100%)**
  - Priority Score: **2,914 points** | Tour Distance: **259 km** (55 unique stops)
  - Total Runtime: **58.621 ms**

The dual-panel visual chart is saved to [`runtime.png`](file:///c:/Users/shrey/ADA/courier_planner/runtime.png).

---

## 6. Sample Output Walkthrough (`small.json`)

```
===========================================================================
STAGE 1: MERGE SORT (Deadline Ascending, Priority Descending)
===========================================================================
Top 10 Sorted Parcels:
Rank  ID      Deadline    Priority    Weight (kg)   Destination Node
-----------------------------------------------------------------
1     P#2     2           13          4             Node 6
2     P#10    2           11          6             Node 4
3     P#4     2           6           1             Node 2
4     P#9     4           14          5             Node 7
5     P#1     5           6           2             Node 2
6     P#8     7           15          1             Node 3
7     P#6     9           17          9             Node 4
8     P#5     10          37          4             Node 1
9     P#7     10          33          4             Node 3
10    P#3     10          10          9             Node 4

===========================================================================
STAGE 2: 0/1 KNAPSACK SELECTION (Dynamic Programming)
===========================================================================
Selected: P#2, P#10, P#4, P#9, P#8, P#5, P#7 (7 parcels)
Total Priority Value: 129 pts | Weight Utilized: 25 / 25 kg (100%)

===========================================================================
STAGE 3: ROUTING (Dijkstra Shortest Paths + Nearest-Neighbor TSP)
===========================================================================
Delivery Stop Sequence:
  Depot(0) -> Node 1 -> Node 6 -> Node 2 -> Node 3 -> Node 7 -> Node 4 -> Depot(0)

Detailed Road-Network Navigation:
  0 -> 1 -> 6 -> 2 -> 3 -> 0 -> 7 -> 5 -> 4 -> 0
Total Round-Trip Distance: 122 km
```

---

## 7. Advanced Optimization Ideas & Comparative Studies (from `report.md`)

1. **TSP: Nearest-Neighbor vs. 2-Opt vs. Held-Karp:**
   - *2-Opt Local Search:* Iteratively reverses tour sub-segments $(i, j)$ to eliminate edge crossings; improves NN tours by 8–15% in $<5$ ms.
   - *Held-Karp Exact DP:* Provides globally optimal tours in $O(K^2 2^K)$ for small stop counts ($K \le 20$).
   - *Christofides-Serdyukov:* Guarantees a $\le 1.5 \times \text{OPT}$ metric TSP approximation via MST and minimum weight perfect matching.
2. **Shortest Path: Dijkstra vs. $A^*$ Search:**
   - Incorporating GPS Euclidean/Haversine distance heuristics $h(u) \le d^*(u, \text{goal})$ reduces explored search space by up to 80%.
3. **Knapsack: 0/1 DP vs. Greedy Density:**
   - Sorting by $v_i / w_i$ provides a fast 2-approximation in $O(N \log N)$ and $O(1)$ auxiliary space, achieving 96.1% of global optimum on the benchmark dataset.
4. **Logistics Domain Extension:**
   - Transitioning from independent Knapsack + TSP to the integrated **Vehicle Routing Problem with Time Windows (VRPTW)** with arrival time penalties.

---

## 8. Quick Commands Reference

```bash
# 1. Run pipeline on small dataset (with DP table)
python courier_planner/main.py --dataset small

# 2. Run pipeline on large dataset (500 parcels)
python courier_planner/main.py --dataset large

# 3. Run benchmark suite & regenerate runtime.png
python courier_planner/benchmark.py

# 4. Regenerate random datasets
python courier_planner/parcels.py
```

