Gesture Control
A real-time gesture detection program using Python, OpenCV. The model was trained on Google Colab and detects hands in a webcam feed with high accuracy.

Features
Real-time hand detection using YOLOv5
Custom-trained model for improved accuracy
Processes live video feed using OpenCV
Efficient and optimized for real-time performance
Requirements
Ensure you have the following dependencies installed:

pip install torch torchvision opencv-python numpy
You also need to clone the YOLOv5 repository if you haven't already:

git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
Usage
Run the script to start real-time hand detection:

python hand_detection.py
Make sure your trained YOLOv5 model is placed correctly in the project directory.

How It Works
Captures video from the webcam using OpenCV
Loads a custom YOLOv5 model trained on hand images
Detects hands in real time and draws bounding boxes
Runs efficiently on CPU/GPU for smooth performance
Notes
Model was trained using Google Colab with a custom dataset
GPU acceleration is recommended for optimal performance
Adjust confidence thresholds as needed for different environments
