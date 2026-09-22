"""Generates the 20x20 Mars terrain grid used by the simulator.

The terrain is a simple grid of cell types. Each cell type has a
"movement cost" that the rover pays to drive across it, except for
rocks and craters which the rover cannot cross at all.
"""

from __future__ import annotations

import random
from typing import TypedDict

# Terrain size. A 20x20 grid is small enough to render clearly on a
# school laptop but large enough to make pathfinding interesting.
GRID_WIDTH: int = 20
GRID_HEIGHT: int = 20

# Cell type names used throughout the app and sent to the browser.
EMPTY = "empty"
ROCK = "rock"
CRATER = "crater"
SAND = "sand"

# How much it "costs" the rover to drive across each terrain type.
# Rocks and craters are not included here because the rover can never
# drive across them (see is_passable below).
TERRAIN_MOVEMENT_COST: dict[str, int] = {
    EMPTY: 1,
    SAND: 3,
}

# Roughly what fraction of the map should be covered by each obstacle.
ROCK_COVERAGE = 0.15
CRATER_COVERAGE = 0.08
SAND_COVERAGE = 0.20


class Position(TypedDict):
    """A simple x/y coordinate on the terrain grid."""

    x: int
    y: int


def is_passable(cell_type: str) -> bool:
    """Return True if the rover is physically able to drive on this cell."""
    return cell_type not in (ROCK, CRATER)


def movement_cost(cell_type: str) -> int:
    """Return how many 'energy points' it costs to move onto this cell."""
    return TERRAIN_MOVEMENT_COST.get(cell_type, 1)


def _random_cell_type() -> str:
    """Pick a random terrain type, weighted so obstacles are less common."""
    roll = random.random()
    if roll < ROCK_COVERAGE:
        return ROCK
    if roll < ROCK_COVERAGE + CRATER_COVERAGE:
        return CRATER
    if roll < ROCK_COVERAGE + CRATER_COVERAGE + SAND_COVERAGE:
        return SAND
    return EMPTY


def _build_random_grid(width: int, height: int) -> list[list[str]]:
    """Create a grid of random terrain types."""
    return [[_random_cell_type() for _ in range(width)] for _ in range(height)]


def _grid_has_path(
    grid: list[list[str]], start: tuple[int, int], goal: tuple[int, int]
) -> bool:
    """Quick reachability check (plain BFS) used only during generation."""
    width, height = len(grid[0]), len(grid)
    visited = {start}
    frontier = [start]
    while frontier:
        x, y = frontier.pop()
        if (x, y) == goal:
            return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                if is_passable(grid[ny][nx]):
                    visited.add((nx, ny))
                    frontier.append((nx, ny))
    return False


def generate_terrain(
    width: int = GRID_WIDTH, height: int = GRID_HEIGHT
) -> tuple[list[list[str]], Position, Position]:
    """Generate a new terrain grid with a rover start and a science target.

    The generator keeps retrying until it produces a map where the target
    can actually be reached, so students never get stuck with an
    impossible puzzle.
    """
    for _ in range(200):  # generous retry limit, generation is very fast
        grid = _build_random_grid(width, height)

        rover_start = (0, 0)
        target = (width - 1, height - 1)

        # The rover's start and the science target must always be clear.
        grid[rover_start[1]][rover_start[0]] = EMPTY
        grid[target[1]][target[0]] = EMPTY

        if _grid_has_path(grid, rover_start, target):
            rover_position: Position = {"x": rover_start[0], "y": rover_start[1]}
            target_position: Position = {"x": target[0], "y": target[1]}
            return grid, rover_position, target_position

    # Extremely unlikely fallback: an empty map is always solvable.
    grid = [[EMPTY for _ in range(width)] for _ in range(height)]
    return grid, {"x": 0, "y": 0}, {"x": width - 1, "y": height - 1}
