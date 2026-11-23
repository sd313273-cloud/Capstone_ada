"""
knapsack.py - 0/1 Knapsack Dynamic Programming for Courier Vehicle Loading.

Selects the subset of parcels that maximizes total priority value without exceeding
the vehicle's weight capacity W. Includes DP table visualization for small instances
and optimal parcel reconstruction backtracking.
"""

from typing import List, Tuple

try:
    from courier_planner.parcels import Parcel
except ImportError:
    from parcels import Parcel


def print_dp_table(dp: List[List[int]], parcels: List[Parcel], capacity: int) -> None:
    """
    Renders the 2D Dynamic Programming table in a clean, human-readable ASCII format.

    Args:
        dp: 2D table of dimensions (N+1) x (W+1).
        parcels: List of Parcel items.
        capacity: Maximum capacity W.
    """
    print("\n" + "=" * 70)
    print("0/1 KNAPSACK DYNAMIC PROGRAMMING TABLE")
    print("=" * 70)
    print("Rows: Items considered (0 = no items, i = up to parcel i)")
    print("Cols: Current capacity constraint (0 to W)\n")

    # Determine column width based on maximum value and capacity
    col_width = 4
    header = f"{'Item (ID, W, V)':<20} |" + "".join(f"{c:>{col_width}}" for c in range(capacity + 1))
    print(header)
    print("-" * len(header))

    # Base row (i = 0)
    base_row = f"{'0: [No Items]':<20} |" + "".join(f"{dp[0][c]:>{col_width}}" for c in range(capacity + 1))
    print(base_row)

    # Item rows (i = 1 to N)
    for i, p in enumerate(parcels, start=1):
        item_label = f"{i}: P#{p.id} (w={p.weight}, v={p.value})"
        row_str = f"{item_label:<20} |" + "".join(f"{dp[i][c]:>{col_width}}" for c in range(capacity + 1))
        print(row_str)

    print("=" * 70 + "\n")


def solve_knapsack(parcels: List[Parcel], capacity: int,
                   print_table: bool = False) -> Tuple[List[Parcel], int, int]:
    """
    Solves the 0/1 Knapsack problem using Dynamic Programming.

    Mathematical Formulation:
        Let DP[i][w] = maximum priority value obtainable using a subset of the
                       first i parcels with total weight <= w.

        Recurrence:
            DP[0][w] = 0                       for 0 <= w <= W
            DP[i][0] = 0                       for 0 <= i <= N
            DP[i][w] = DP[i-1][w]              if parcels[i-1].weight > w
            DP[i][w] = max(DP[i-1][w],
                           DP[i-1][w - weight_i] + value_i) otherwise

    Complexity:
        Time Complexity:  O(N * W) where N is number of parcels and W is vehicle capacity.
        Space Complexity: O(N * W) for the 2D DP matrix.

    Args:
        parcels: List of Parcel objects available for loading.
        capacity: Maximum weight capacity of the delivery vehicle.
        print_table: If True, prints the full DP table (recommended for small N and W).

    Returns:
        Tuple of (selected_parcels, total_value, total_weight).
    """
    n = len(parcels)

    # Allocate (n + 1) x (capacity + 1) 2D table initialized to 0
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # Populate DP table row by row
    for i in range(1, n + 1):
        p = parcels[i - 1]
        weight = p.weight
        val = p.value

        for w in range(capacity + 1):
            if weight > w:
                # Parcel is too heavy to fit into current weight limit w
                dp[i][w] = dp[i - 1][w]
            else:
                # Option 1: Do not include parcel i (keep value from previous i-1)
                without_item = dp[i - 1][w]
                # Option 2: Include parcel i (add parcel value + best value of remaining weight)
                with_item = dp[i - 1][w - weight] + val

                dp[i][w] = without_item if without_item > with_item else with_item

    # Print DP table if requested (or auto-format for small inputs)
    if print_table:
        print_dp_table(dp, parcels, capacity)

    # Backtracking to reconstruct the optimal subset of parcels chosen
    selected_parcels: List[Parcel] = []
    curr_w = capacity
    for i in range(n, 0, -1):
        # If the value changed from dp[i-1][curr_w], item i was included
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            chosen_parcel = parcels[i - 1]
            selected_parcels.append(chosen_parcel)
            curr_w -= chosen_parcel.weight

    # Reverse to restore original chronological/sorted sequence
    selected_parcels.reverse()

    total_value = dp[n][capacity]
    total_weight = sum(p.weight for p in selected_parcels)

    return selected_parcels, total_value, total_weight


if __name__ == "__main__":
    # Self-test using a small set of parcels
    sample_parcels = [
        Parcel(id=1, weight=3, value=25, deadline=1, dest_node=2),
        Parcel(id=2, weight=2, value=20, deadline=2, dest_node=3),
        Parcel(id=3, weight=4, value=30, deadline=3, dest_node=1),
        Parcel(id=4, weight=1, value=15, deadline=4, dest_node=5),
        Parcel(id=5, weight=5, value=40, deadline=5, dest_node=4),
    ]
    test_capacity = 8

    chosen, max_val, total_wt = solve_knapsack(sample_parcels, test_capacity, print_table=True)
    print(f"Optimal Total Value:  {max_val}")
    print(f"Total Weight Used:    {total_wt} / {test_capacity} kg")
    print(f"Selected Parcels:     {[f'P#{p.id} (w={p.weight}, v={p.value})' for p in chosen]}")

