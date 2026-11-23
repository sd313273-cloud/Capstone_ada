"""
sorting.py - Custom Merge Sort implementation for parcel prioritization.

Sorts parcels by:
1. Delivery deadline (ascending - earliest deadline has highest urgency).
2. Priority/Value (descending - higher value processed first for identical deadlines).

Strict Requirement: No built-in Python sort() or sorted() used.
"""

from typing import List

try:
    from courier_planner.parcels import Parcel
except ImportError:
    from parcels import Parcel


def is_before(a: Parcel, b: Parcel) -> bool:
    """
    Comparison predicate for ordering two parcels.

    Rules:
    - Primary: Earlier deadline comes first (ascending).
    - Secondary: Higher priority/value comes first when deadlines are tied (descending).
    - Tie-break: Lower parcel ID (deterministic ordering).

    Returns:
        True if parcel 'a' should strictly precede parcel 'b', False otherwise.
    """
    if a.deadline < b.deadline:
        return True
    elif a.deadline > b.deadline:
        return False

    # Deadlines are equal: compare priority/value (descending)
    if a.value > b.value:
        return True
    elif a.value < b.value:
        return False

    # Values are equal: deterministic tie-break by ID (ascending)
    return a.id < b.id


def merge(left: List[Parcel], right: List[Parcel]) -> List[Parcel]:
    """
    Merges two sorted lists into a single sorted list.

    Time Complexity: O(len(left) + len(right))
    Space Complexity: O(len(left) + len(right))
    """
    merged: List[Parcel] = []
    i = 0  # Pointer for left list
    j = 0  # Pointer for right list

    while i < len(left) and j < len(right):
        if is_before(left[i], right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append any remaining elements from left or right half
    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged


def merge_sort(parcels: List[Parcel]) -> List[Parcel]:
    """
    Sorts a list of parcels using the classical divide-and-conquer Merge Sort.

    Algorithm Steps:
    1. Divide: Split the unsorted list into two approximately equal halves.
    2. Conquer: Recursively sort each half until sublists have size <= 1.
    3. Combine: Merge the sorted sublists into a final sorted output.

    Complexity:
        Time Complexity: O(N log N) in all cases (best, average, worst).
        Space Complexity: O(N) auxiliary memory for sublists during recursion.

    Args:
        parcels: List of Parcel objects to sort.

    Returns:
        A new list containing the parcels in sorted order.
    """
    # Base case: a list of 0 or 1 element is already sorted
    if len(parcels) <= 1:
        return list(parcels)

    # Divide: Find midpoint and split into two halves
    mid = len(parcels) // 2
    left_half = parcels[:mid]
    right_half = parcels[mid:]

    # Conquer: Recursively sort both halves
    sorted_left = merge_sort(left_half)
    sorted_right = merge_sort(right_half)

    # Combine: Merge the two sorted halves
    return merge(sorted_left, sorted_right)


if __name__ == "__main__":
    # Self-test with sample parcels
    test_parcels = [
        Parcel(id=1, weight=5, value=20, deadline=4, dest_node=2),
        Parcel(id=2, weight=3, value=35, deadline=2, dest_node=3),
        Parcel(id=3, weight=2, value=15, deadline=2, dest_node=1),  # Same deadline as id 2, lower value
        Parcel(id=4, weight=6, value=40, deadline=1, dest_node=4),
    ]

    sorted_list = merge_sort(test_parcels)
    print("Self-test merge_sort output:")
    for p in sorted_list:
        print(f"  Parcel {p.id}: Deadline={p.deadline}, Value={p.value}, Weight={p.weight}")
