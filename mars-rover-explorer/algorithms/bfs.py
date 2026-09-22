"""Breadth First Search (BFS) pathfinding for the Mars rover.

BFS explores the terrain one 'ring' of distance at a time. It always
finds the shortest path in terms of number of steps, but it does not
know which direction is closer to the target - it just spreads out
evenly in every direction, like ripples in a pond.
"""

from __future__ import annotations

from collections import deque
from typing import TypedDict

from algorithms.terrain import is_passable

Coordinate = tuple[int, int]


class ExplorationStep(TypedDict):
    """One moment in the search, used by the browser to animate BFS."""

    x: int
    y: int
    state: str  # "frontier" (queued) or "visited" (fully explored)


class SearchResult(TypedDict):
    """Everything the frontend needs to draw and explain the search."""

    found: bool
    path: list[dict[str, int]]
    steps: list[ExplorationStep]
    cells_explored: int


def _neighbours(x: int, y: int, width: int, height: int) -> list[Coordinate]:
    """Return the up/down/left/right neighbours that are inside the grid."""
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(nx, ny) for nx, ny in candidates if 0 <= nx < width and 0 <= ny < height]


def breadth_first_search(
    grid: list[list[str]], start: Coordinate, goal: Coordinate
) -> SearchResult:
    """Search for a path from start to goal, exploring layer by layer."""
    height = len(grid)
    width = len(grid[0]) if height else 0

    queue: deque[Coordinate] = deque([start])
    came_from: dict[Coordinate, Coordinate] = {}
    visited: set[Coordinate] = {start}
    steps: list[ExplorationStep] = []

    goal_found = False
    while queue:
        current = queue.popleft()
        steps.append({"x": current[0], "y": current[1], "state": "visited"})

        if current == goal:
            goal_found = True
            break

        for neighbour in _neighbours(current[0], current[1], width, height):
            nx, ny = neighbour
            if neighbour in visited:
                continue
            if not is_passable(grid[ny][nx]):
                continue
            visited.add(neighbour)
            came_from[neighbour] = current
            queue.append(neighbour)
            steps.append({"x": nx, "y": ny, "state": "frontier"})

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
        "cells_explored": len(visited),
    }
