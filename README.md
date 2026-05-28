# Pneuma Reach

Pneuma Reach is an experimental, bare-hand gesture control interface for Windows, designed with an ergonomic "Anchor Lock" mechanism to eliminate anatomical cursor drop. Built with Python, OpenCV, MediaPipe, and PyQt6, it offers a seamless, Sci-Fi HUD-inspired experience.

## Features

- **Ergonomic Anchor Lock:** Tracks the index finger's base knuckle (`index_mcp`) during a pinch to perfectly freeze the cursor, solving the typical "downward slide" found in most bare-hand tracking implementations.
- **Hysteresis Thresholding:** Uses strict 3D distance to initiate a click (pinch), and a forgiving 2D distance to maintain the drag, making it immune to camera occlusion and Z-axis noise when fingers cross.
- **Minimalist HUD:** Custom PyQt6 and OpenCV overlay that applies a frosted glassmorphism effect, hiding unnecessary skeletal data to focus strictly on user immersion and accuracy.
- **EMA Smoothing:** Applies Exponential Moving Average filtering to eliminate hand jitter and provide buttery-smooth mouse control.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Astrelio/Pneuma.git
   cd Pneuma
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure that the `hand_landmarker.task` model is present in the `detector/` directory.

## Usage

Run the main script to start the interface:
```bash
python main.py
```

### Gestures

- **Hover:** Move your open hand in front of the camera. The cursor tracks the tip of your index finger.
- **Click & Drag (Pinch):** Bring your index finger and thumb together. The cursor will lock in place (Anchor Lock) ensuring pinpoint accuracy. Keep them pinched to drag windows or files.
- **Exit:** Click on the HUD overlay and press the `Q` or `Esc` key on your keyboard to close the application safely.

## Architecture

- `main.py`: The core PyQt6 application and camera loop.
- `detector/`: MediaPipe models and the gesture classification math.
- `controller/`: PyAutoGUI wrapper for mapping camera coordinates to the OS cursor.
- `ui/`: OpenCV UI drawing (`hud.py`) and PyQt6 transparent overlay (`overlay.py`).

## License
MIT License
