# VisionPlay: AI-Powered Football Analytics

---

## 🎯 Project Motivation

Manual analysis of football matches is time-consuming and error-prone. VisionPlay leverages state-of-the-art computer vision techniques to automate this process, offering fast, accurate, and insightful analysis.

---

## 🧠 Problem Statement

VisionPlay aims to streamline football video analysis by automatically detecting and tracking players, referees, and the ball using YOLO for object detection and Deep SORT for multi-object tracking. This eliminates the need for manual tagging and provides real-time insights.

---

## 🏆 Objectives

- **Player Detection & Tracking** using YOLOv11.
- **Multi-object tracking** of players, referees, and the ball.
- **Insight generation** based on spatial and temporal tracking data.

---

## ✅ Functional Requirements

- Detect players using YOLO.
- Pause tracking when an object exits the field.
- Zoom in on the player in possession of the ball.
- Distinguish between players and referees.

---

## 🔧 Non-Functional Requirements

- High accuracy in detection and classification.
- User-friendly UI for controlling and visualizing tracking and insights.

---

## 🔄 System Design

- **Activity Diagram** – Describes the dynamic workflow of the tracking system.
- **Sequence Diagram** – Illustrates interaction between modules.

---

## 💻 User Interface

The system includes an intuitive dashboard that displays:
- Live tracking view
- Heatmaps
- Player statistics
- Match insights

---

## 📊 Output Features

- **Heatmaps** – Visual representation of player movements.
- **Insights** – Key metrics like possession time, player coverage, etc.

---

## 🚀 Technologies Used

- **Object Detection**: YOLOv11
- **Multi-Object Tracking**: Deep SORT
- **Frontend**: (Add if applicable)
- **Backend/Processing**: Python, OpenCV, NumPy, etc.

---

## 📁 How to Run (Add as per implementation)

```bash
# Clone the repo
git clone https://github.com/Harshavardhan-Sondakar/VisionPlay.git
cd visionplay

# Install dependencies
pip install -r requirements.txt

# Run the frontend Streamlit app
streamlit run frontend/index.py