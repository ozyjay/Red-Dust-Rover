# How This App Is Running (Simple Explanation)

This document explains, in plain terms, how the Red Dust Rover app works
right now while you're testing it locally.

## 1. It's a Flask web server

`app.py` starts a small Python web server using Flask. When you run:

```bash
python3 app.py
```

Flask starts listening on your own computer at:

```
http://127.0.0.1:5000
```

`127.0.0.1` means "this computer" (also called `localhost`). Nothing is
uploaded to the internet - the whole app runs locally on your machine.

## 2. The browser talks to Flask, Flask talks back with HTML/JSON

- When you open `http://127.0.0.1:5000/` in a browser, Flask runs the
  `home()` function in [app.py](app.py) and sends back
  the rendered `index.html` page.
- When you click "Launch the Simulator", the browser asks for
  `/simulator`, and Flask sends back `simulator.html`.
- These HTML pages load Bootstrap (for styling) and `simulator.js` (for the
  interactive canvas grid) from the `static/` folder.

## 3. The simulator page calls a mini "API" for data

The HTML page itself doesn't know how to generate terrain or run
pathfinding - it asks the Flask server for that data using `fetch()` calls
in `simulator.js`. These are the four endpoints Flask exposes:

| Your browser asks for... | Flask runs...                | Flask sends back...                |
|---------------------------|-------------------------------|-------------------------------------|
| `GET /api/generate`       | `generate_terrain()`          | A new random 20x20 grid, rover start, target |
| `POST /api/astar`         | `a_star_search()`             | Path, exploration steps, stats     |
| `POST /api/bfs`           | `breadth_first_search()`      | Path, exploration steps, stats     |
| `GET /api/fact`           | picks a random Mars fact      | One fact string                    |

All of these responses are plain JSON (text data) - no database is
involved. Everything is calculated fresh, in memory, each time you click a
button.

## 4. There is no database and no saved state

- Nothing is written to disk.
- Nothing is remembered between page refreshes or server restarts.
- Every time you click "Generate New Terrain", a brand new random grid is
  created on the spot and sent to your browser.

## 5. The browser does all the drawing and animating

Once `simulator.js` receives the JSON data from Flask, it draws everything
itself using the HTML `<canvas>` element:

- Colours the grid squares (rock, crater, sand, empty).
- Draws the rover and target icons.
- Reveals the algorithm's explored cells step by step.
- Animates the rover moving along the final path.

Flask never draws anything - it only calculates the terrain and the
algorithm results and hands the numbers over as JSON.

## 6. Debug mode is on

Because `app.run(debug=True)` is used in `app.py`, Flask automatically
restarts itself whenever you save a change to a Python file, so you can see
your edits immediately without manually restarting the server. This is only
meant for local development, not for a real public website.

## Quick mental model

```
Your Browser  <---HTML/JS/CSS--->  Flask Server (app.py)
     |                                     |
     |  fetch('/api/generate')             |
     |  fetch('/api/astar', ...)   ------->|--> algorithms/astar.py
     |  fetch('/api/bfs', ...)     ------->|--> algorithms/bfs.py
     |  fetch('/api/fact')                 |
     |<---------------- JSON data ---------|
     |
  Canvas draws the grid, rover, and path
```

In short: **Flask serves the pages and does the "thinking" (pathfinding
math); the browser does all the drawing and animation, talking to Flask
through small JSON API calls.**
