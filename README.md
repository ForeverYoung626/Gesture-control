# Gesture Control

Gesture Control is a Python-based project that uses computer vision to detect hand gestures via a webcam and map them to system control actions. The project leverages OpenCV, MediaPipe, and PyAutoGUI for real-time gesture recognition and automation.

## Features
- Real-time hand gesture detection and classification
- Supports multiple control actions (e.g., volume adjustment, media play/pause, navigation)
- Cross-platform support (Windows, macOS, Linux)
- Extendable for custom gesture mappings

## Technologies Used
- Python 3.8+
- OpenCV - video processing and camera streaming
- MediaPipe - hand landmark detection
- PyAutoGUI - automation for keyboard and mouse control

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/ForeverYoung626/Gesture-control.git
cd Gesture-control
```

### 2. Create and activate a virtual environment
```
python -m venv venv
# On macOS / Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
## Usage
Run the main script:
```
python main.py
```
