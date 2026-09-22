# 🔴 Red Dust Rover

An interactive Flask web app that teaches school students (Years 5-9) how
autonomous Mars rovers navigate around obstacles using real search
algorithms - **Breadth First Search** and **A\*** - instead of lectures.

Students generate a random 20x20 Mars terrain full of rocks, craters, and
sand, then watch the rover explore the map and plan a route to a science
target, with a side panel explaining what the algorithm is "thinking" as it
runs.

## Features

- 🌍 Randomly generated 20x20 Mars terrain (rocks, craters, sand, empty ground)
- 🎨 HTML Canvas visualisation with an animated rover
- 🧭 Breadth First Search and A* (Manhattan distance heuristic) pathfinding
- 👣 Step-through mode to study the algorithm one cell at a time
- 🧠 A live "What is happening?" explanation panel written for students
- 🏆 Challenge Mode stats: path length, cells explored, and time taken
- 📡 Random real Mars facts panel
- 🌄 Bonus: a "realistic background" rendering mode for the terrain canvas

## Project structure

```
red-dust-rover/
│
├── app.py                  # Flask app and REST API endpoints
├── requirements.txt
│
├── static/
│   ├── css/style.css       # Styling for the site
│   ├── js/simulator.js     # Canvas rendering, animation, and API calls
│   └── images/             # Optional background image for the bonus mode
│
├── templates/
│   ├── base.html           # Shared page layout (navbar, Bootstrap, footer)
│   ├── index.html          # Home page
│   └── simulator.html      # Simulator page
│
└── algorithms/
    ├── terrain.py          # Terrain generation and movement rules
    ├── bfs.py              # Breadth First Search implementation
    └── astar.py            # A* implementation
```

## REST API

| Method | Endpoint       | Description                                      |
|--------|----------------|---------------------------------------------------|
| GET    | `/api/generate`| Generates a new random terrain grid               |
| POST   | `/api/astar`   | Runs A* on a given grid/rover/target, returns JSON |
| POST   | `/api/bfs`     | Runs BFS on a given grid/rover/target, returns JSON|
| GET    | `/api/fact`    | Returns one random Mars fact                       |

All endpoints return JSON. `astar` and `bfs` expect a JSON body like:

```json
{
  "grid": [["empty", "rock", ...], ...],
  "rover": {"x": 0, "y": 0},
  "target": {"x": 19, "y": 19}
}
```

and respond with the found path, a step-by-step exploration trace (for
animation), and stats (`path_length`, `cells_explored`, `time_taken_ms`).

## Setup instructions

Requires **Python 3.12+**.

```bash
cd red-dust-rover
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run instructions

```bash
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

You'll land on the welcome page - click **"Launch the Simulator"** to open
the interactive Mars terrain, generate new maps, and run the algorithms.

## Classroom challenge

> Can you design terrain that tricks the rover into taking a longer path?

Generate several terrains and compare the **path length**, **cells
explored**, and **time taken** between A* and BFS. Which algorithm explores
fewer cells? Why might that matter for a real rover with limited battery
power?
