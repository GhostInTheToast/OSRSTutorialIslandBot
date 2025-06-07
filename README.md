# Old School RuneScape Tutorial Island Completer

A Python script that helps automate the Tutorial Island completion in Old School RuneScape by detecting red objects in the game window.

## Features

- Real-time red object detection in the game window
- Region of interest (ROI) monitoring
- Visual feedback with bounding boxes
- Coordinate finder tool for setting up monitoring regions

## Requirements

- Python 3.x
- OpenCV
- PyAutoGUI
- Quartz (for macOS)
- NumPy

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd OldSchoolRunescapeTutorialIslandCompleter
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the coordinate finder to determine the region you want to monitor:
```bash
python coordinate_finder.py
```

2. Run the color detector with your chosen coordinates:
```bash
python color_detector.py
```

## Controls

- Press 'q' to quit the program
- Press 'c' in the coordinate finder to capture coordinates

## Note

Make sure to grant screen recording permissions to your terminal/IDE on macOS for the script to work properly. 