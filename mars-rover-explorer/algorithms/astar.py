"""A* pathfinding for the Mars rover, using the Manhattan distance heuristic.

A* is smarter than BFS because it uses a "guess" (the heuristic) of how
far each cell is from the target. Cells that seem closer to the target
are explored first, so A* usually finds a good path while looking at
far fewer cells than BFS.
"""

from __future__ import annotations

import heapq
from typing import TypedDict

from algorithms.terrain import is_passable, movement_cost

Coordinate = tuple[int, int]


class ExplorationStep(TypedDict):
    """One moment in the search, used by the browser to animate A*."""

    x: int
    y: int
    state: str  # "open" (candidate) or "closed" (fully evaluated)


class SearchResult(TypedDict):
    """Everything the frontend needs to draw and explain the search."""

    found: bool
    path: list[dict[str, int]]
    steps: list[ExplorationStep]
    cells_explored: int


def manhattan_distance(a: Coordinate, b: Coordinate) -> int:
    """Estimate the distance between two points, moving only in straight lines.

    This matches how the rover actually moves (up/down/left/right), so the
    estimate never overestimates the true cost - which is what makes A*
    guaranteed to find the shortest path.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbours(x: int, y: int, width: int, height: int) -> list[Coordinate]:
    """Return the up/down/left/right neighbours that are inside the grid."""
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(nx, ny) for nx, ny in candidates if 0 <= nx < width and 0 <= ny < height]


def a_star_search(
    grid: list[list[str]], start: Coordinate, goal: Coordinate
) -> SearchResult:
    """Search for the cheapest path from start to goal using A*."""
    height = len(grid)
    width = len(grid[0]) if height else 0

    # The priority queue orders cells by "estimated total cost" (f_score).
    # A tie-breaking counter keeps heapq happy when f_scores are equal.
    counter = 0
    open_heap: list[tuple[int, int, Coordinate]] = [
        (manhattan_distance(start, goal), counter, start)
    ]
    came_from: dict[Coordinate, Coordinate] = {}

    # g_score = cheapest known cost from start to this cell.
    g_score: dict[Coordinate, int] = {start: 0}
    in_open_set: set[Coordinate] = {start}
    closed_set: set[Coordinate] = set()
    steps: list[ExplorationStep] = []

    goal_found = False
    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current in closed_set:
            continue  # a cheaper copy of this cell was already processed

        in_open_set.discard(current)
        closed_set.add(current)
        steps.append({"x": current[0], "y": current[1], "state": "closed"})

        if current == goal:
            goal_found = True
            break

        for neighbour in _neighbours(current[0], current[1], width, height):
            nx, ny = neighbour
            if neighbour in closed_set:
                continue
            if not is_passable(grid[ny][nx]):
                continue

            tentative_g = g_score[current] + movement_cost(grid[ny][nx])
            if tentative_g < g_score.get(neighbour, float("inf")):
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbour, goal)
                counter += 1
                heapq.heappush(open_heap, (f_score, counter, neighbour))
                if neighbour not in in_open_set:
                    in_open_set.add(neighbour)
                    steps.append({"x": nx, "y": ny, "state": "open"})

    path: list[dict[str, int]] = []
    if goal_found:
        node = goal
        while node != start:
            path.append({"x": node[0], "y": node[1]})
            node = came_from[node]
        path.append({"x": start[0], "y": start[1]})
        path.reverse()

    return {
        "found": goal_found,
        "path": path,
        "steps": steps,
        "cells_explored": len(closed_set),
    }
