# Mini-Courier Planner (ADA Capstone Project)

A modular, end-to-end algorithmic system for optimal last-mile parcel dispatch and courier route scheduling. This project integrates four core Design and Analysis of Algorithms (DAA) paradigms into a cohesive logistics decision pipeline:

1. **Divide-and-Conquer:** Custom Merge Sort for multi-criteria deadline & priority sorting.
2. **Dynamic Programming:** 0/1 Knapsack for value-maximizing vehicle payload selection within weight constraints.
3. **Greedy Graph Traversal:** Min-heap Dijkstra for single-source and all-pairs shortest paths across road networks.
4. **Heuristic Approximation:** Nearest-Neighbor Traveling Salesperson Problem (TSP) for round-trip route synthesis.

---

## 1. System Architecture & Workflow

```
[ Raw Parcel Orders & Road Graph (data/*.json) ]
                       │
                       ▼
         ┌───────────────────────────┐
         │ Stage 1: Custom Merge Sort│  Primary: Deadline (asc)
         │       (sorting.py)        │  Secondary: Priority (desc)
         └─────────────┬─────────────┘
                       │ Sorted Inventory
                       ▼
         ┌───────────────────────────┐
         │  Stage 2: 0/1 Knapsack DP │  Vehicle capacity constraint W
         │       (knapsack.py)       │  DP Table printed for small input
         └─────────────┬─────────────┘
                       │ Selected High-Value Parcels
                       ▼
         ┌───────────────────────────┐
         │  Stage 3: Dijkstra (heapq)│  Shortest paths across road network
         │        (graph.py)         │  Computes metric distance matrix
         └─────────────┬─────────────┘
                       │ All-Pairs Shortest Distances & Paths
                       ▼
         ┌───────────────────────────┐
         │ Stage 4: Nearest-Neighbor │  Round-trip tour from Depot (0)
         │       TSP (tsp.py)        │  Returns full road traversal & total km
         └─────────────┬─────────────┘
                       │
                       ▼
         [ Final Courier Dispatch Manifest & Navigation Plan ]
```

---

## 2. Algorithms & Complexity Summary

| Pipeline Stage | Module | Algorithmic Paradigm | Time Complexity (Best/Worst) | Space Complexity | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Parcel Ordering** | `sorting.py` | Divide & Conquer (Merge Sort) | $\Theta(N \log N)$ | $O(N)$ | Sorts orders without built-in `sort()`; strictly prioritizes early deadlines and high values. |
| **Cargo Loading** | `knapsack.py` | Dynamic Programming (0/1 Knapsack) | $O(N \cdot W)$ | $O(N \cdot W)$ | Optimally packs vehicle capacity $W$ to maximize total delivery value. |
| **Pathfinding** | `graph.py` | Greedy with Min-Heap (Dijkstra) | $O((V + E) \log V)$ per source | $O(V)$ | Finds shortest road distances and intermediate junctions between stops. |
| **Route Synthesis**| `tsp.py` | Greedy Approximation (Nearest Neighbor) | $O(K^2)$ for $K$ destinations | $O(K)$ | Constructs closed delivery circuit starting and finishing at Depot (Node 0). |


## 3. Project Directory Structure

```
courier_planner/
├── __init__.py           # Package declaration
├── parcels.py            # Parcel dataclass, graph generator, JSON serializer/deserializer
├── sorting.py            # From-scratch Merge Sort implementation (no built-in sort)
├── knapsack.py           # 0/1 Knapsack DP with table printer and backtracking
├── graph.py              # Dijkstra's shortest path with heapq and predecessor tracking
├── tsp.py                # Nearest-Neighbor TSP tour approximation
├── main.py               # End-to-end orchestration CLI
├── benchmark.py          # Empirical time.perf_counter benchmark suite & chart generator
├── runtime.png           # Exported runtime scaling chart
├── README.md             # Project documentation and guide
├── report.md             # In-depth algorithmic design report & comparative analysis
└── data/
    ├── small.json        # 10 parcels, 8 nodes, W = 25 kg
    └── large.json        # 500 parcels, 100 nodes, W = 150 kg
```

---



## 4. Sample Execution Output

### Small Dataset (`small.json`)
```
###########################################################################
       MINI-COURIER PLANNER: DAA CAPSTONE OPTIMIZATION PIPELINE
###########################################################################

[+] Loading problem instance from: courier_planner/data/small.json
    - Total Parcels Available: 10
    - Network Nodes (Junctions): 8 (Depot = Node 0)
    - Delivery Vehicle Capacity: 25 kg

===========================================================================
STAGE 1: MERGE SORT (Deadline Ascending, Priority Descending)
===========================================================================
Top 10 Sorted Parcels (Primary: Deadline, Secondary: Priority):
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
Selecting maximum-value parcel subset within vehicle capacity W = 25 kg...

0/1 KNAPSACK DYNAMIC PROGRAMMING TABLE
Rows: Items considered (0 = no items, i = up to parcel i)
Cols: Current capacity constraint (0 to W)

Item (ID, W, V)      |   0   1   2   3   4   5  ...  23  24  25
---------------------------------------------------------------
0: [No Items]        |   0   0   0   0   0   0  ...   0   0   0
1: P#2 (w=4, v=13)   |   0   0   0   0  13  13  ...  13  13  13
2: P#10 (w=6, v=11)  |   0   0   0   0  13  13  ...  24  24  24
...
9: P#7 (w=4, v=33)   |   0  15  21  21  37  52  ... 124 124 129
10: P#3 (w=9, v=10)  |   0  15  21  21  37  52  ... 124 124 129

[Knapsack Optimization Result]
  - Parcels Accepted for Loading: 7 of 10
  - Total Priority Value:          129 pts
  - Total Weight Utilized:         25 / 25 kg (100.0%)
  - Remaining Vehicle Capacity:    0 kg

Loaded Cargo Manifest:
ID      Weight    Priority    Deadline    Destination Node
-------------------------------------------------------
P#2     4         13          2           Node 6
P#10    6         11          2           Node 4
P#4     1         6           2           Node 2
P#9     5         14          4           Node 7
P#8     1         15          7           Node 3
P#5     4         37          10          Node 1
P#7     4         33          10          Node 3

===========================================================================
STAGE 3: ROUTING (Dijkstra Shortest Paths + Nearest-Neighbor TSP)
===========================================================================
Delivery Stop Sequence (7 legs):
  Depot(0) -> Node 1 -> Node 6 -> Node 2 -> Node 3 -> Node 7 -> Node 4 -> Depot(0)

Leg-by-Leg Details:
  Leg  1: Depot(0)   --> Node 1     | Distance:   4 km | Cum:   4 km
  Leg  2: Node 1     --> Node 6     | Distance:  13 km | Cum:  17 km
  Leg  3: Node 6     --> Node 2     | Distance:   9 km | Cum:  26 km
  Leg  4: Node 2     --> Node 3     | Distance:  12 km | Cum:  38 km
  Leg  5: Node 3     --> Node 7     | Distance:  39 km | Cum:  77 km
  Leg  6: Node 7     --> Node 4     | Distance:  22 km | Cum:  99 km
  Leg  7: Node 4     --> Depot(0)   | Distance:  23 km | Cum: 122 km

Detailed Road-Network Navigation (All Junctions Traversed):
  0 -> 1 -> 6 -> 2 -> 3 -> 0 -> 7 -> 5 -> 4 -> 0

Total Round-Trip Distance: 122 km
```

---

## 5. Verification and Tests

All modules include standalone unit self-tests that can be executed directly:
- `python courier_planner/sorting.py`: Verifies Merge Sort ordering and tie-breaking.
- `python courier_planner/knapsack.py`: Verifies DP recurrence, table rendering, and item recovery.
- `python courier_planner/graph.py`: Verifies Dijkstra shortest distance and path backtracking.
- `python courier_planner/tsp.py`: Verifies nearest-neighbor tour construction.
