"""Red Dust Rover - a Flask web app that teaches students how
autonomous rovers navigate obstacles using search algorithms.

Run with:

    python app.py

Then open http://127.0.0.1:5000 in a browser.
"""

from __future__ import annotations

import random
import time

from flask import Flask, jsonify, render_template, request

from algorithms.astar import a_star_search
from algorithms.bfs import breadth_first_search
from algorithms.terrain import GRID_HEIGHT, GRID_WIDTH, generate_terrain

app = Flask(__name__)

# Fun, real facts about Mars exploration shown in the "Real Mars Facts" panel.
# Kept in Python (not a database) to keep the project simple for students.
MARS_FACTS: list[str] = [
    "Radio signals can take between 4 and 24 minutes to travel between "
    "Earth and Mars, so rovers must make some decisions on their own.",
    "NASA's Perseverance rover landed in Jezero Crater, an ancient dry lake bed.",
    "Mars rovers cannot use GPS - there is no satellite network around Mars "
    "for navigation, so they rely on cameras and onboard computers.",
    "The Curiosity rover has been driving on Mars since August 2012.",
    "Mars has huge dust storms that can sometimes cover the entire planet.",
    "A day on Mars (called a 'sol') is about 24 hours and 39 minutes long.",
    "Mars rovers use special wheels designed to cope with sharp volcanic rocks.",
    "Olympus Mons on Mars is the largest volcano in the solar system - almost "
    "three times taller than Mount Everest.",
    "Rovers plan safe routes ahead of time because Mars has no roads, "
    "signposts, or maps drawn by humans.",
    "The Ingenuity helicopter was the first aircraft to fly on another planet.",
]


def _validate_grid(grid: object) -> list[list[str]] | None:
    """Check that the client sent a well-formed rectangular terrain grid."""
    if not isinstance(grid, list) or len(grid) != GRID_HEIGHT:
        return None
    for row in grid:
        if not isinstance(row, list) or len(row) != GRID_WIDTH:
            return None
        if not all(isinstance(cell, str) for cell in row):
            return None
    return grid


def _validate_position(position: object) -> tuple[int, int] | None:
    """Check that a position dict has integer x/y coordinates inside the grid."""
    if not isinstance(position, dict):
        return None
    x, y = position.get("x"), position.get("y")
    if not isinstance(x, int) or not isinstance(y, int):
        return None
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return None
    return x, y


@app.route("/")
def home() -> str:
    """Welcoming home page that explains the mission."""
    return render_template("index.html")


@app.route("/simulator")
def simulator() -> str:
    """The interactive Mars terrain simulator."""
    return render_template("simulator.html")


@app.route("/api/generate", methods=["GET"])
def api_generate():
    """Generate a brand new random terrain, rover start, and target."""
    grid, rover, target = generate_terrain()
    return jsonify(
        {
            "grid": grid,
            "rover": rover,
            "target": target,
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT,
        }
    )


@app.route("/api/fact", methods=["GET"])
def api_fact():
    """Return one random Mars fact for the educational side panel."""
    return jsonify({"fact": random.choice(MARS_FACTS)})


def _run_search(algorithm_name: str):
    """Shared request handling for the /api/astar and /api/bfs endpoints."""
    data = request.get_json(silent=True) or {}

    grid = _validate_grid(data.get("grid"))
    rover = _validate_position(data.get("rover"))
    target = _validate_position(data.get("target"))

    if grid is None or rover is None or target is None:
        return jsonify({"error": "Invalid grid, rover, or target in request."}), 400

    start_time = time.perf_counter()
    if algorithm_name == "astar":
        result = a_star_search(grid, rover, target)
    else:
        result = breadth_first_search(grid, rover, target)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    result["time_taken_ms"] = round(elapsed_ms, 3)
    result["path_length"] = len(result["path"])

    return jsonify(result)


@app.route("/api/astar", methods=["POST"])
def api_astar():
    """Run A* search and return the path plus animation steps."""
    return _run_search("astar")


@app.route("/api/bfs", methods=["POST"])
def api_bfs():
    """Run Breadth First Search and return the path plus animation steps."""
    return _run_search("bfs")


if __name__ == "__main__":
    app.run(debug=True)
