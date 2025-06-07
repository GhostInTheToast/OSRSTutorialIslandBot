# Old School RuneScape Tutorial Island Bot

This project aims to automate the Tutorial Island experience in Old School RuneScape (2004Scape) using computer vision and automation techniques.

## Features

### Color Detection Tool
- Real-time detection of red objects in the game window
- Automatic mouse movement to the largest detected red object
- Visual feedback with green bounding boxes around detected objects
- Configurable detection region and sensitivity

## Requirements

- Python 3.8+
- OpenCV
- NumPy
- PyAutoGUI
- Pynput

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GhostInTheToast/OSRSTutorialIslandBot.git
cd OSRSTutorialIslandBot
```

2. Create and activate a virtual environment:
```bash
python -m venv osrsBotting
source osrsBotting/bin/activate  # On Windows: osrsBotting\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Color Detection Tool
Run the color detection script:
```bash
python color_detector.py
```

Controls:
- Press '1' to move the mouse to the largest red object
- Press 'q' to quit the program

The tool will:
1. Monitor the specified region of the game window
2. Detect red objects in real-time
3. Display green boxes around detected objects
4. Move the mouse to the largest red object when requested

## Development Status

Currently in active development. The color detection tool is functional and can be used to detect and interact with red objects in the game window.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 