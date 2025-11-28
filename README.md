# Cube AI Live Solver

A desktop application that uses computer vision to scan a physical 3×3 Rubik's Cube, reconstruct its state, solve it using the Kociemba algorithm, and provide real-time solving guidance through a webcam feed.

## Overview

This project provides a simple 2D computer vision overlay (no AR/VR, no markers, no headsets) that:
- Captures all 6 faces of a Rubik's Cube via webcam
- Reconstructs the cube state as a 54-character Kociemba format string
- Computes an optimal solution using the Kociemba algorithm
- Displays real-time solving suggestions with visual overlays in an OpenCV window

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Scan the Cube Faces
Capture all 6 faces of your Rubik's Cube:
```bash
python src/scanner.py
```

Follow the on-screen instructions to align each face (U, R, F, D, L, B) inside the grid and press SPACE to capture. The scan data will be saved to `data/cube_scan.json`.

### Step 2: Build the Cube State
Convert the scanned faces into a Kociemba state string:
```bash
python src/state_builder.py
```

This will classify colors and generate a 54-character state string, saved to `data/cube_state.txt`.

### Step 3: (Optional) View the Solution
Preview the solution moves:
```bash
python src/solver.py
```

Or pass a state string directly:
```bash
python src/solver.py "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
```

### Step 4: Get Live Solving Guidance
Start the interactive solver with real-time camera overlay:
```bash
python src/live_guidance.py
```

The application will:
- Display your webcam feed with a 3×3 grid overlay
- Show the current move instruction (e.g., "Step 3 / 21: R'")
- Draw visual arrows indicating which face to turn and in which direction
- Press SPACE to confirm you've executed each move
- Press Q to quit at any time

## Technical Notes

- **No AR/VR**: This is a simple 2D OpenCV overlay only. It does not use AR frameworks, VR, 3D engines, or marker-based tracking.
- **Color Classification**: Uses HSV color space with Euclidean distance matching
- **Solver**: Implements the Kociemba two-phase algorithm for optimal solutions
- **Camera**: Uses the default webcam (index 0)

## Project Structure

```
cube-ai-live-solver/
├── README.md
├── requirements.txt
├── src/
│   ├── scanner.py          # Face capture with webcam
│   ├── color_classifier.py # HSV to color mapping
│   ├── state_builder.py    # Kociemba string construction
│   ├── solver.py           # Kociemba solver wrapper
│   ├── live_guidance.py    # Main interactive loop
│   └── utils.py            # Shared helper functions
└── data/
    ├── cube_scan.json      # Scanned face data (generated)
    ├── cube_state.txt      # Cube state string (generated)
    └── samples/            # Optional debug images
```

## Requirements

- Python 3.10+
- Webcam
- Physical 3×3 Rubik's Cube

