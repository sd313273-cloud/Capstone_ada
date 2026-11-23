# Mini-Courier Planner: Algorithmic Design, Empirical Evaluation, and Optimization Report

**Author:** Shreyash (DAA Capstone Project)  
**Date:** November 2026  
**Subject:** Design and Analysis of Algorithms (DAA)  

---

## 1. Executive Summary & Problem Formulation

Last-mile courier logistics is one of the most computationally demanding challenges in supply chain optimization, representing over 40% of total package delivery costs. The operational cycle requires answering three sequential questions under hard physical constraints:
1. **Prioritization:** Given hundreds of pending parcels with heterogeneous urgency deadlines and customer priority ratings, in what order should orders be evaluated?
2. **Capacity Allocation:** Given a vehicle with maximum physical payload capacity $W$, which subset of parcels should be loaded to maximize total delivered priority value without exceeding capacity?
3. **Route Synthesis:** Given the geographic drop-off locations of selected parcels and a street network graph with intermediate intersections, what is the optimal sequence of delivery stops and the exact road path that minimizes total fuel consumption and round-trip driving distance?

The **Mini-Courier Planner** addresses this problem by harmonizing four foundational algorithmic paradigms into a unified, pipeline-driven engine:

```
Unsorted Parcels & Graph
          │
          ▼
   [ Merge Sort ] ────────► Stable O(N log N) ordering by deadline & priority
          │
          ▼
 [ 0/1 Knapsack DP ] ─────► Optimal pseudo-polynomial O(N·W) payload selection
          │
          ▼
  [ Dijkstra (heapq) ] ───► Shortest-path metric graph construction O(K · (V+E) log V)
          │
          ▼
[ Nearest-Neighbor TSP ] ─► Greedy route approximation O(K^2) with full path synthesis
          │
          ▼
Dispatched Manifest & Route
```

---

## 2. In-Depth Algorithmic Design & Theoretical Analysis

### 2.1 Module 1: Parcel Sorting (`sorting.py`)
- **Paradigm:** Divide-and-Conquer (Merge Sort).
- **Design Decision & Motivation:** 
  Standard Python `list.sort()` was explicitly prohibited. QuickSort exhibits an $O(N^2)$ worst-case degeneration on pre-sorted or adversarial inputs. HeapSort, while $O(N \log N)$, is not a stable sort. **Merge Sort** was selected because:
  1. It provides a guaranteed worst-case time bound of $\Theta(N \log N)$.
  2. It is strictly **stable**, meaning parcels with identical deadlines and priorities preserve their relative submission order.
- **Multi-Criteria Comparison Predicate:**
  $$\text{IsBefore}(A, B) \iff (d_A < d_B) \lor (d_A = d_B \land v_A > v_B) \lor (d_A = d_B \land v_A = v_B \land \text{id}_A < \text{id}_B)$$
  where $d$ is delivery deadline, $v$ is priority value, and $\text{id}$ is the unique identifier for deterministic tie-breaking.
- **Recurrence & Complexity:**
  $$T(N) = 2T(N/2) + \Theta(N) \implies T(N) = \Theta(N \log N) \quad \text{(Master Theorem Case 2)}$$
  Auxiliary memory is $O(N)$ for merging temporary sublists.

---

### 2.2 Module 2: Cargo Payload Selection (`knapsack.py`)
- **Paradigm:** Dynamic Programming (0/1 Knapsack).
- **Design Decision & Motivation:**
  Fractional packing is unacceptable in parcel delivery (a courier cannot deliver half a laptop). The 0/1 Knapsack problem is NP-complete. However, in logistical dispatch, the vehicle capacity $W$ is bounded (e.g., $25 \text{ kg} \le W \le 200 \text{ kg}$), making pseudo-polynomial Dynamic Programming optimal and blazingly fast.
- **Bellman Recurrence:**
  Let $DP[i][w]$ be the maximum priority value achievable using a subset of the first $i$ parcels with total weight at most $w$:
  $$DP[i][w] = \begin{cases} 
  0 & \text{if } i = 0 \text{ or } w = 0 \\
  DP[i-1][w] & \text{if } w_i > w \\
  \max\big(DP[i-1][w], \, DP[i-1][w - w_i] + v_i\big) & \text{if } w_i \le w 
  \end{cases}$$
- **Backtracking & Parcel Recovery:**
  To identify the actual parcels loaded, the algorithm traces backwards from $(N, W)$:
  $$\text{If } DP[i][w] \ne DP[i-1][w], \text{ then parcel } i \text{ was selected; set } w \leftarrow w - w_i$$
- **Complexity:**
  - Time Complexity: $\Theta(N \cdot W)$ operations.
  - Space Complexity: $O(N \cdot W)$ for the full 2D table (which allows full reconstruction and small-instance table visualization).

---

### 2.3 Module 3: Network Pathfinding (`graph.py`)
- **Paradigm:** Greedy Shortest Path with Binary Min-Heap (Dijkstra).
- **Design Decision & Motivation:**
  Road networks contain positive physical distances ($w(u, v) > 0$). Bellman-Ford ($O(VE)$) is unnecessarily slow without negative cycles, while unweighted BFS cannot account for varying road segment lengths.
- **Implementation Highlights:**
  Using Python’s `heapq` module, Dijkstra's algorithm manages active edge relaxations in $O(\log V)$ per vertex extract. Lazy deletion discards suboptimal distance pairs already superseded in the priority queue. Predecessor pointers $\pi[v]$ record the shortest-path tree, enabling recovery of intermediate road junctions.
- **All-Pairs Metric Closure:**
  Rather than computing all-pairs shortest paths across the entire graph with Floyd-Warshall ($O(V^3)$), Dijkstra is executed only for the $K + 1$ locations of interest (Depot + $K$ distinct delivery nodes), yielding:
  $$T_{\text{dijkstra}} = (K + 1) \cdot O((V + E) \log V)$$

---

### 2.4 Module 4: Route Synthesis (`tsp.py`)
- **Paradigm:** Greedy Approximation (Nearest-Neighbor Heuristic).
- **Design Decision & Motivation:**
  The Traveling Salesperson Problem on $K$ stops is strongly NP-hard. Exact algorithms (e.g., Held-Karp $O(K^2 2^K)$ or branch-and-bound) become intractable when $K > 25$. For real-time courier dispatch where plans must generate in milliseconds, the **Nearest-Neighbor (NN)** heuristic provides an effective $O(K^2)$ solution.
- **Algorithm Flow:**
  1. Start tour at Depot $u = 0$.
  2. At each step, select unvisited destination $v^* = \arg\min_{v \in \text{Unvisited}} \text{dist}(u, v)$.
  3. Append intermediate vertices from `path_matrix[u][v*]` into the complete road navigation log.
  4. Once all stops are visited, close the tour by returning to Depot.
- **Approximation Ratio:**
  On general metric spaces satisfying the triangle inequality, Nearest Neighbor yields an approximation ratio bounded by $O(\log K)$, providing practical routes within 10–20% of optimal in sub-millisecond time.

---

## 3. Empirical Benchmark Results

### 3.1 Experimental Configuration
- **Hardware/OS:** Windows x86_64, Intel Core Architecture.
- **Software:** Python 3.13.14 (CPython runtime), `time.perf_counter()` high-precision timing.
- **Sample Trials:** 5 independent runs per problem size, reporting arithmetic mean latency.
- **Visualization:** Matplotlib dual-panel plot saved to `runtime.png`.

---

### 3.2 Benchmark Latency Table

| Input Scale ($N$) | Nodes ($V$) | Vehicle Cap ($W$) | Merge Sort (ms) | 0/1 Knapsack (ms) | Dijkstra (ms) | TSP NN (ms) | Total Pipeline (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 8 | 25 kg | 0.0255 ms | 0.0645 ms | 0.0834 ms | 0.0097 ms | **0.1831 ms** |
| **50** | 10 | 25 kg | 0.1278 ms | 0.2907 ms | 0.1938 ms | 0.0194 ms | **0.6318 ms** |
| **100** | 20 | 33 kg | 0.2924 ms | 0.8957 ms | 0.8739 ms | 0.0430 ms | **2.1050 ms** |
| **200** | 40 | 66 kg | 0.8432 ms | 3.1165 ms | 4.7645 ms | 0.1820 ms | **8.9062 ms** |
| **500** | 100 | 166 kg | 1.9565 ms | 22.9689 ms | 41.5610 ms | 0.6082 ms | **67.0946 ms** |

### Standard Pre-Generated Datasets

| Dataset | Available Parcels | Delivered Parcels | Weight Used | Priority Score | Tour Distance | Total Runtime |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`small.json`** | 10 | 7 | 25 / 25 kg (100%) | 129 pts | 122 km | **0.277 ms** |
| **`large.json`** | 500 | 85 | 150 / 150 kg (100%) | 2914 pts | 259 km | **58.621 ms** |

---

### 3.3 Performance Observations
1. **Knapsack Bilinear Growth:** The knapsack execution time scaled from $0.065 \text{ ms}$ at $(N=10, W=25)$ to $22.97 \text{ ms}$ at $(N=500, W=166)$, closely matching the theoretical $O(N \cdot W)$ complexity curve.
2. **Dijkstra Dominance on Large Graphs:** In the 500-parcel instance with 100 road junctions and 55 unique delivery stops, running multi-source Dijkstra took $41.56 \text{ ms}$, accounting for ~62% of the overall dispatch computation.
3. **Efficiency of Nearest-Neighbor TSP:** Despite routing across 55 unique destinations, the Nearest-Neighbor tour assembly completed in just $0.61 \text{ ms}$ due to the $O(K^2)$ distance lookup structure.

---

## 4. Advanced Algorithmic Optimizations & Comparisons

### 4.1 TSP Routing: Nearest-Neighbor vs. 2-Opt vs. Held-Karp

| Strategy | Paradigm | Time Complexity | Optimality Guarantee | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Nearest-Neighbor (Current)** | Greedy Heuristic | $O(K^2)$ | $O(\log K)$ approximation | Ultra-fast initial route generation ($< 1 \text{ ms}$). |
| **2-Opt Local Search** | Iterative Improvement | $O(K^2 \text{ per pass})$ | Local optimum (eliminates edge crossings) | Post-processing heuristic: improves NN tours by 8–15% in $< 5 \text{ ms}$. |
| **Christofides-Serdyukov** | MST + Matching | $O(K^3)$ | Guaranteed $\le 1.5 \times \text{OPT}$ | Metric TSP requiring certified worst-case quality. |
| **Held-Karp Exact DP** | Dynamic Programming | $O(K^2 2^K)$ | Global Optimum | Small instances ($K \le 20$). |

#### Implementing 2-Opt Post-Processing
Nearest-Neighbor often produces self-crossing paths when returning to the depot. A **2-Opt** pass tests every pair of non-adjacent tour edges $(u_i, u_{i+1})$ and $(u_j, u_{j+1})$. If reversing the sub-tour segment between $i+1$ and $j$ reduces cumulative distance:
$$\Delta D = \big(\text{dist}(u_i, u_j) + \text{dist}(u_{i+1}, u_{j+1})\big) - \big(\text{dist}(u_i, u_{i+1}) + \text{dist}(u_j, u_{j+1})\big) < 0$$
then the segment is reversed. Repeating until no negative $\Delta D$ exists yields a 2-optimal tour in milliseconds.

---

### 4.2 Pathfinding: Dijkstra vs. A* vs. Contraction Hierarchies

| Algorithm | Paradigm | Time Complexity | Prerequisite / Heuristic | Benefit in Logistics |
| :--- | :--- | :--- | :--- | :--- |
| **Dijkstra (Current)** | Uniform-cost search | $O((V+E)\log V)$ | Non-negative edge weights | Guaranteed shortest paths; foundational baseline. |
| **A\* Search** | Directed Heuristic Search | $O(E)$ best case | Admissible heuristic $h(u) \le d^*(u, \text{goal})$ | Focuses search cone towards destination using Euclidean/Haversine distance; expands up to 80% fewer nodes. |
| **Contraction Hierarchies** | Node contraction index | $O(\log V)$ per query | $O(V \log V + E)$ offline preprocessing | State-of-the-art for continental road graphs (OpenStreetMap); sub-millisecond point-to-point queries. |

In an expanded system with GPS coordinates, substituting Dijkstra with **$A^*$** equipped with the Haversine distance heuristic would substantially reduce node expansions across dense urban grids.

---

### 4.3 Cargo Selection: 0/1 DP vs. Greedy Density vs. Branch & Bound

| Knapsack Method | Exact/Approx | Time Complexity | Space Complexity | Practical Trade-off |
| :--- | :--- | :--- | :--- | :--- |
| **0/1 DP (Current)** | Exact | $O(N \cdot W)$ | $O(N \cdot W)$ (or $O(W)$) | Optimal value; suitable for integer capacities. |
| **Greedy Ratio ($v_i/w_i$)** | 2-Approximation | $O(N \log N)$ | $O(1)$ | Near-instantaneous; optimal for Fractional Knapsack; guaranteed $\ge 50\%$ optimal for 0/1. |
| **Branch and Bound** | Exact | $O(2^N)$ worst case | $O(N)$ | Fast for large $W$ where $N \cdot W$ exceeds memory, pruning via fractional upper bounds. |

#### Empirical Ratio Comparison
For the small dataset ($W = 25$):
- **0/1 DP Optimum:** Value = **129** (utilizes 25 kg).
- **Greedy Density Heuristic:** Sorting items by $v_i / w_i$ yields Value = **124** (utilizes 24 kg), reaching **96.1% of global optimum** in negligible time.

---

### 4.4 Domain Extension: Vehicle Routing Problem with Time Windows (VRPTW)
In production distribution systems, parcel deadlines represent physical delivery time windows $[e_i, l_i]$. A promising extension to the pipeline:
1. Augment edge travel costs with estimated travel time $t(u, v) = \text{dist}(u, v) / \text{speed}$.
2. Enforce arrival time $T_{\text{arr}}(v) = \max\big(e_v, T_{\text{arr}}(u) + t(u, v) + t_{\text{service}}\big)$.
3. Impose steep penalty costs if $T_{\text{arr}}(v) > l_v$, seamlessly bridging Knapsack prioritization with real-world time-window constraints.

---

## 5. Conclusion

The **Mini-Courier Planner** demonstrates how modular algorithm design enables an elegant and computationally efficient solution to an NP-hard logistics pipeline. By layering stable Merge Sort, pseudo-polynomial 0/1 Knapsack DP, priority-queued Dijkstra pathfinding, and Nearest-Neighbor TSP approximation, the system processes a 500-parcel distribution network in under **68 milliseconds**. The addition of 2-Opt local search and $A^*$ heuristic evaluation represents a direct and viable path to industrial-scale route planning.

