/**
 * Mars Rover Explorer - simulator front-end.
 *
 * Handles: drawing the terrain grid on a canvas, calling the Flask API to
 * generate terrain and run search algorithms, and animating the results so
 * students can see how BFS and A* explore the map.
 */

const CANVAS = document.getElementById("terrain-canvas");
const CTX = CANVAS.getContext("2d");

const TERRAIN_COLOURS = {
    empty: "#d9a066",
    sand: "#e6c766",
    rock: "#4a4a4a",
    crater: "#7a4a2b",
};

// Colours used to overlay the algorithm's progress on top of the terrain.
const FRONTIER_COLOUR = "rgba(241, 196, 15, 0.75)"; // BFS frontier / A* open set
const VISITED_COLOUR = "rgba(133, 193, 232, 0.7)"; // BFS visited / A* closed set
const PATH_COLOUR = "rgba(255, 255, 255, 0.9)";

// Friendly, student-facing explanations shown while an algorithm runs.
const EXPLANATIONS = {
    bfs: {
        frontier: "The rover is exploring possible routes in every direction - BFS checks nearby cells first.",
        visited: "This cell has now been fully checked by Breadth First Search.",
    },
    astar: {
        frontier: "A* is looking for paths that seem closer to the target.",
        visited: "A* has confirmed this is the best known route to this cell so far.",
    },
};

/** Holds everything we know about the current simulation. */
const state = {
    grid: [],
    rover: { x: 0, y: 0 },
    target: { x: 0, y: 0 },
    width: 20,
    height: 20,
    cellSize: 30,
    searchResult: null, // last response from /api/astar or /api/bfs
    stepIndex: 0, // how many exploration steps have been revealed so far
    lastAlgorithm: "astar",
    animationTimer: null,
    realisticBackground: false,
    backgroundTexture: null, // offscreen canvas used by the bonus mode
};

/**
 * Bonus feature: generate a speckled reddish-brown texture that looks more
 * like a real Mars photo than flat colour squares. Drawn once per terrain
 * and cached, since it is only decorative and never changes the pathfinding.
 */
function generateBackgroundTexture() {
    const texture = document.createElement("canvas");
    texture.width = CANVAS.width;
    texture.height = CANVAS.height;
    const textureCtx = texture.getContext("2d");

    const gradient = textureCtx.createRadialGradient(
        CANVAS.width / 2, CANVAS.height / 2, 0,
        CANVAS.width / 2, CANVAS.height / 2, CANVAS.width / 1.2
    );
    gradient.addColorStop(0, "#c1662f");
    gradient.addColorStop(1, "#7a3312");
    textureCtx.fillStyle = gradient;
    textureCtx.fillRect(0, 0, texture.width, texture.height);

    // Scatter small speckles so the surface looks dusty and uneven.
    for (let i = 0; i < 1500; i += 1) {
        const px = Math.random() * texture.width;
        const py = Math.random() * texture.height;
        const shade = Math.random() > 0.5 ? "rgba(0,0,0,0.08)" : "rgba(255,200,150,0.08)";
        textureCtx.fillStyle = shade;
        textureCtx.fillRect(px, py, 2, 2);
    }

    state.backgroundTexture = texture;
}

function setExplanation(message) {
    document.getElementById("explanation-text").textContent = message;
}

function setStats({ pathLength, cellsExplored, timeTakenMs }) {
    document.getElementById("stat-path-length").textContent = pathLength ?? "-";
    document.getElementById("stat-cells-explored").textContent = cellsExplored ?? "-";
    document.getElementById("stat-time-taken").textContent = timeTakenMs ?? "-";
}

/** Draw the base terrain (no algorithm overlay), rover, and target. */
function drawBaseTerrain() {
    const size = state.cellSize;

    if (state.realisticBackground && state.backgroundTexture) {
        CTX.drawImage(state.backgroundTexture, 0, 0);
    }

    for (let y = 0; y < state.height; y += 1) {
        for (let x = 0; x < state.width; x += 1) {
            const cellType = state.grid[y][x];

            if (state.realisticBackground) {
                // Only draw overlays for obstacles/sand; empty cells show the texture.
                if (cellType === "rock") {
                    CTX.fillStyle = "rgba(40, 40, 40, 0.55)";
                    CTX.fillRect(x * size, y * size, size, size);
                } else if (cellType === "crater") {
                    CTX.fillStyle = "rgba(30, 15, 5, 0.5)";
                    CTX.beginPath();
                    CTX.arc(x * size + size / 2, y * size + size / 2, size * 0.42, 0, Math.PI * 2);
                    CTX.fill();
                } else if (cellType === "sand") {
                    CTX.fillStyle = "rgba(230, 199, 102, 0.35)";
                    CTX.fillRect(x * size, y * size, size, size);
                }
            } else {
                CTX.fillStyle = TERRAIN_COLOURS[cellType] ?? TERRAIN_COLOURS.empty;
                CTX.fillRect(x * size, y * size, size, size);
            }

            CTX.strokeStyle = "rgba(0, 0, 0, 0.15)";
            CTX.strokeRect(x * size, y * size, size, size);
        }
    }
}

/** Draw the exploration overlay (frontier/visited or open/closed cells). */
function drawExploredSteps(stepsToShow) {
    const size = state.cellSize;
    stepsToShow.forEach((step) => {
        const isFrontier = step.state === "frontier" || step.state === "open";
        CTX.fillStyle = isFrontier ? FRONTIER_COLOUR : VISITED_COLOUR;
        CTX.fillRect(step.x * size, step.y * size, size, size);
    });
}

/** Draw the final path found by the algorithm. */
function drawPath(path) {
    const size = state.cellSize;
    CTX.fillStyle = PATH_COLOUR;
    path.forEach((cell) => {
        const padding = size * 0.3;
        CTX.fillRect(
            cell.x * size + padding,
            cell.y * size + padding,
            size - padding * 2,
            size - padding * 2
        );
    });
}

/** Draw a rover icon centred on a given grid cell. */
function drawRover(position) {
    const size = state.cellSize;
    const centreX = position.x * size + size / 2;
    const centreY = position.y * size + size / 2;

    CTX.fillStyle = "#1d6fe0";
    CTX.beginPath();
    CTX.arc(centreX, centreY, size * 0.32, 0, Math.PI * 2);
    CTX.fill();
    CTX.fillStyle = "white";
    CTX.font = `${Math.floor(size * 0.5)}px sans-serif`;
    CTX.textAlign = "center";
    CTX.textBaseline = "middle";
    CTX.fillText("🤖", centreX, centreY + 1);
}

/** Draw the science target icon on a given grid cell. */
function drawTarget(position) {
    const size = state.cellSize;
    const centreX = position.x * size + size / 2;
    const centreY = position.y * size + size / 2;

    CTX.fillStyle = "#2ecc71";
    CTX.beginPath();
    CTX.arc(centreX, centreY, size * 0.32, 0, Math.PI * 2);
    CTX.fill();
    CTX.fillStyle = "white";
    CTX.font = `${Math.floor(size * 0.5)}px sans-serif`;
    CTX.textAlign = "center";
    CTX.textBaseline = "middle";
    CTX.fillText("🎯", centreX, centreY + 1);
}

/** Full redraw: terrain, any revealed search steps, path, target, and rover. */
function render(roverOverride) {
    drawBaseTerrain();

    if (state.searchResult) {
        const steps = state.searchResult.steps.slice(0, state.stepIndex);
        drawExploredSteps(steps);

        if (state.stepIndex >= state.searchResult.steps.length && state.searchResult.found) {
            drawPath(state.searchResult.path);
        }
    }

    drawTarget(state.target);
    drawRover(roverOverride ?? state.rover);
}

/** Fetch a brand new terrain map from the server and reset the simulation. */
async function loadNewTerrain() {
    stopAnimation();
    const response = await fetch("/api/generate");
    const data = await response.json();

    state.grid = data.grid;
    state.rover = data.rover;
    state.target = data.target;
    state.width = data.width;
    state.height = data.height;
    state.cellSize = CANVAS.width / state.width;
    state.searchResult = null;
    state.stepIndex = 0;
    generateBackgroundTexture();

    setStats({ pathLength: "-", cellsExplored: "-", timeTakenMs: "-" });
    setExplanation("A fresh Mars terrain has landed! Choose an algorithm to see the rover plan a route.");
    render();
}

function stopAnimation() {
    if (state.animationTimer) {
        clearInterval(state.animationTimer);
        state.animationTimer = null;
    }
}

/** Call the backend to run a search algorithm and store the result. */
async function fetchSearchResult(algorithm) {
    const response = await fetch(`/api/${algorithm}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grid: state.grid, rover: state.rover, target: state.target }),
    });
    const result = await response.json();

    state.searchResult = result;
    state.stepIndex = 0;
    state.lastAlgorithm = algorithm;

    setStats({
        pathLength: result.path_length,
        cellsExplored: result.cells_explored,
        timeTakenMs: result.time_taken_ms,
    });

    return result;
}

/** Move the rover icon smoothly (cell by cell) along the found path. */
function animateRoverAlongPath(path) {
    let stepIndex = 0;
    const moveTimer = setInterval(() => {
        if (stepIndex >= path.length) {
            clearInterval(moveTimer);
            setExplanation("Success! The rover followed the path all the way to the science target. 🎉");
            return;
        }
        render(path[stepIndex]);
        stepIndex += 1;
    }, 180);
}

/** Reveal every exploration step automatically, then animate the rover's path. */
function runAndAnimate(algorithm) {
    stopAnimation();
    fetchSearchResult(algorithm).then((result) => {
        const messages = EXPLANATIONS[algorithm];
        let revealed = 0;

        state.animationTimer = setInterval(() => {
            if (revealed >= result.steps.length) {
                clearInterval(state.animationTimer);
                state.animationTimer = null;
                state.stepIndex = result.steps.length;

                if (result.found) {
                    animateRoverAlongPath(result.path);
                } else {
                    setExplanation("No path was found - the target is completely boxed in by rocks and craters!");
                }
                return;
            }

            const step = result.steps[revealed];
            state.stepIndex = revealed + 1;
            render();
            setExplanation(messages[step.state] ?? "The rover is exploring possible routes.");
            revealed += 1;
        }, 25);
    });
}

/** Reveal exactly one exploration step per click, for careful step-by-step study. */
async function stepThroughAlgorithm() {
    stopAnimation();

    if (!state.searchResult) {
        await fetchSearchResult(state.lastAlgorithm);
        setExplanation("Search started! Keep clicking 'Step Through Algorithm' to explore one cell at a time.");
        render();
        return;
    }

    const { steps, path, found } = state.searchResult;

    if (state.stepIndex < steps.length) {
        const step = steps[state.stepIndex];
        state.stepIndex += 1;
        render();
        const messages = EXPLANATIONS[state.lastAlgorithm];
        setExplanation(messages[step.state] ?? "The rover is exploring possible routes.");
        return;
    }

    if (found) {
        render();
        setExplanation("All cells explored! The white path shows the route the rover will drive.");
    } else {
        setExplanation("No path was found - the target is completely boxed in by rocks and craters!");
    }
}

function resetSimulation() {
    stopAnimation();
    state.searchResult = null;
    state.stepIndex = 0;
    setStats({ pathLength: "-", cellsExplored: "-", timeTakenMs: "-" });
    setExplanation("Simulation reset. Press a Run button to start a new search.");
    render();
}

async function loadRandomFact() {
    const response = await fetch("/api/fact");
    const data = await response.json();
    document.getElementById("mars-fact-text").textContent = data.fact;
}

document.getElementById("btn-generate").addEventListener("click", loadNewTerrain);
document.getElementById("btn-astar").addEventListener("click", () => runAndAnimate("astar"));
document.getElementById("btn-bfs").addEventListener("click", () => runAndAnimate("bfs"));
document.getElementById("btn-step").addEventListener("click", stepThroughAlgorithm);
document.getElementById("btn-reset").addEventListener("click", resetSimulation);
document.getElementById("btn-new-fact").addEventListener("click", loadRandomFact);
document.getElementById("toggle-realistic-bg").addEventListener("change", (event) => {
    state.realisticBackground = event.target.checked;
    render();
});

// Initial setup when the simulator page loads.
loadNewTerrain();
loadRandomFact();
