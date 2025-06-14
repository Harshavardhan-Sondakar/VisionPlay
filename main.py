from typing import Union, List, Dict  # Add Dict here
import os
import argparse
import warnings
from utils import read_video, save_video, options
from trackers import Tracker
from team_assignment import TeamAssigner
from player_ball_assignment import PlayerBallAssigner
from camera_movement import CameraMovementEstimator
import cv2
import numpy as np  
from insights import InsightsGenerator


def crop_and_zoom(frames: List[np.ndarray], tracks: Dict[str, List[Dict]], ball_possession: np.ndarray) -> List[np.ndarray]:
    """
    Crops and zooms in on the player with the ball.
    """
    zoomed_frames = []

    for frame_num, frame in enumerate(frames):
        frame = frame.copy()
        player_dict = tracks["players"][frame_num]

        # Find the player with the ball
        player_with_ball = None
        for tracker_id, player in player_dict.items():
            if player.get("has_ball", False):
                player_with_ball = player
                break

        if player_with_ball:
            bbox = player_with_ball["bbox"]
            x1, y1, x2, y2 = map(int, bbox)

            # Crop the frame to the bounding box
            cropped_frame = frame[y1:y2, x1:x2]

            # Resize the cropped frame to the original frame size for zoom effect
            zoomed_frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
        else:
            zoomed_frame = frame

        zoomed_frames.append(zoomed_frame)

    return zoomed_frames

def process_video(data: Union[str, bytes], classes: List[int], verbose: bool=True) -> None:
    frames, fps, _, _ = read_video(data, verbose)

    tracker = Tracker("models/best.pt", classes, verbose)
    tracks = tracker.get_object_tracks(frames)
    tracker.add_position_to_tracks(tracks)

    camera_movement_estimator = CameraMovementEstimator(frames[0], classes, verbose)
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(frames)
    camera_movement_estimator.adjust_positions_to_tracks(tracks, camera_movement_per_frame)

    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    team_assigner = TeamAssigner()
    team_assigner.get_teams(frames, tracks)

    player_assigner = PlayerBallAssigner()
    player_assigner.get_player_and_possession(tracks)

    insights_generator = InsightsGenerator()
    insights_generator.generate_all_insights(tracks, player_assigner.ball_possession, fps)

    # Draw annotations on the original frames
    output = tracker.draw_annotations(frames, tracks, player_assigner.ball_possession)
    output = camera_movement_estimator.draw_camera_movement(output, camera_movement_per_frame)

    # Save the normal video
    save_video(output, "output/output_normal.mp4", fps, verbose)

    # Generate zoomed-in video for the player with the ball
    zoomed_output = crop_and_zoom(frames, tracks, player_assigner.ball_possession)
    save_video(zoomed_output, "output/output_zoomed.mp4", fps, verbose)

def _video(path: str) -> None:
    if not path.lower().endswith(".mp4"):
        raise argparse.ArgumentTypeError(f"File '{path}' is not an MP4 file.")
    
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist.") 
    
def _classes(classes: List[str]) -> List[int]:
    class_ids = [value for key, value in options.items() if key in classes]
    
    invalid_classes = [cls for cls in classes if cls not in options.keys()]
    
    # all classes invalid, raise error
    if len(invalid_classes) == len(options):
        raise argparse.ArgumentTypeError("Classes are invalid.")

    # continue with the subset of valid classes
    if invalid_classes:
        warnings.warn(f"Invalid classes: {', '.join(invalid_classes)}. Valid options are: {', '.join(options.keys())}. Continuing with subset of valid classes.")
    
    return class_ids

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MatchVision football analytics.")

    parser.add_argument("--video", type=str, help="Video path of the video (must be .mp4)")
    parser.add_argument("--tracks", nargs="+", type=str, help="Select the objects to visualise: players, goalkeepers, referees, ball")
    parser.add_argument("--verbose", action="store_true", help="Model output and logging")

    args = parser.parse_args()
    
    if args.video and args.tracks:
        _video(args.video)
        classes = _classes(args.tracks)
        
        process_video(args.video, classes, args.verbose)