import streamlit as st
import time
import os
import sys
import pandas as pd
import json
sys.path.append(os.path.abspath("."))
from main import process_video

st.set_page_config(page_title="Football Analysis")

# menu
st.sidebar.title("Settings")

st.sidebar.header("Options")
players = st.sidebar.toggle("Highlight Players", value=True)
goalkeepers = st.sidebar.toggle("Highlight Goalkeepers", value=True)
referees = st.sidebar.toggle("Highlight Referees", value=True)
ball = st.sidebar.toggle("Highlight Ball", value=True)
stats = st.sidebar.toggle("Show Statistics", value=True)

# select classes to track

# data.yaml class IDs
# ball: 0, goalkeeper: 1, player: 2, referee: 3
options = {0: ball, 1: goalkeepers, 2: players, 3: referees, 4: stats}
classes = [key for key, value in options.items() if value is True]

st.sidebar.markdown("***")

st.sidebar.header("Video Source")

st.sidebar.subheader("Demo")

st.sidebar.write("Choose from 2 demo videos.")

uploaded_video = None
demo_video = None
start_analysis = None
processed = False

demo = st.sidebar.toggle("Demo", value=False)

if demo:
    videos = [
    "demos/demo1.mp4",
    "demos/demo2.mp4"
    ]

    demo_video = st.sidebar.radio("Select Video", videos)

    #preview demo video
    st.sidebar.video(demo_video)
    
    if demo_video:
        with open(demo_video, "rb") as f:
            demo_video_bytes = f.read()

    start_analysis = st.sidebar.button("Start Analysis", key="demo")

    if start_analysis:
        with st.spinner("Processing ..."):
            process_video(demo_video_bytes, classes)
            processed = True
        placeholder = st.empty()
        with placeholder.container():
            st.success("Video processing complete.")
            time.sleep(3)
        placeholder.empty()

st.sidebar.write("\n")

st.sidebar.subheader("Video Upload")

uploaded_video = st.sidebar.file_uploader("Select a video file.", type=["mp4"])

if uploaded_video:
    st.sidebar.video(uploaded_video)
    st.sidebar.write("Uploaded video:", uploaded_video.name)
    start_analysis = st.sidebar.button("Start Analysis", key="upload")

    if start_analysis:
        with st.spinner("Processing ..."):
            process_video(uploaded_video.read(), classes) 
            processed = True
        placeholder = st.empty()
        with placeholder.container():
            st.success("Video processing complete.")
            time.sleep(1)
        placeholder.empty()

# main page
st.title("VisionPlay: AI-Powered Football Insights")
# st.subheader("Transforming Football Videos into Actionable Insights with AI and Computer Vision")

tab1, tab2, tab3, tab4 = st.tabs(["Usage", "Results", "Logs", "Insights"])

with tab1:
    st.write("To use the automated analysis, follow these steps:")
    st.markdown("""
    1. Select the desired output options.
    2. Upload a video or select a demo video. 
    3. Click on **Start Analysis**.
    4. Go to the tab **Results** to see the output video.
    5. Go to the tab **Insights** to see the Insights of the Match.
                
    For best results, the video should not contain multiple camera perspectives.
    """)

with tab2:
    if processed:
        st.header("Results")
        st.subheader("Normal Video with Annotations")
        normal_video_path = "output/output_normal.mp4"
        if os.path.exists(normal_video_path):
            st.video(normal_video_path)

        st.subheader("Zoomed-in Video (Player with Ball)")
        zoomed_video_path = "output/output_zoomed.mp4"
        if os.path.exists(zoomed_video_path):
            st.video(zoomed_video_path)

with tab3:
    log_files_list = ["logs/tracking.log", "logs/camera_movement.log", "logs/memory_access.log"]

    selected_log_file = st.selectbox("Select Log File", log_files_list)

    try:
        with open(selected_log_file, "r") as log_file:
            log_contents = log_file.read()
        st.text_area("Logs", log_contents, height=450)
    except FileNotFoundError:
        st.error(f"Log file '{selected_log_file}' not found.")

with tab4:
    st.header("Insights")

    # Display ball possession
    ball_possession_path = "output/insights/ball_possession.json"
    if os.path.exists(ball_possession_path):
        with open(ball_possession_path, "r") as f:
            ball_possession = json.load(f)
        st.subheader("Ball Possession in %")
        st.json(ball_possession)

    # Display player possession
    player_possession_path = "output/insights/player_possession.csv"
    if os.path.exists(player_possession_path):
        player_possession = pd.read_csv(player_possession_path)
        st.subheader("Player Possession Time in sec")
        st.dataframe(player_possession)

    # Display player speed
    player_speed_path = "output/insights/player_speed.csv"
    if os.path.exists(player_speed_path):
        player_speed = pd.read_csv(player_speed_path)
        st.subheader("Player Speed")
        st.dataframe(player_speed)

    # Display team possession
    team_possession_path = "output/insights/team_possession.json"
    if os.path.exists(team_possession_path):
        with open(team_possession_path, "r") as f:
            team_possession = json.load(f)
        st.subheader("Team Possession Time")
        st.json(team_possession)

    # Display heatmaps
    heatmap_path = "output/insights/player_heatmap.png"
    if os.path.exists(heatmap_path):
        st.subheader("Player Movement Heatmap")
        st.image(heatmap_path)

    team1_heatmap_path = "output/insights/team1_heatmap.png"
    if os.path.exists(team1_heatmap_path):
        st.subheader("Team 1 Movement Heatmap")
        st.image(team1_heatmap_path)

    team2_heatmap_path = "output/insights/team2_heatmap.png"
    if os.path.exists(team2_heatmap_path):
        st.subheader("Team 2 Movement Heatmap")
        st.image(team2_heatmap_path)