from typing import Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

class InsightsGenerator:
    def __init__(self, output_dir: str = "output/insights"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def calculate_ball_possession(self, ball_possession: np.ndarray) -> Dict[str, float]:
        """
        Calculate the percentage of ball possession for each team.
        """
        unique, counts = np.unique(ball_possession, return_counts=True)
        total_frames = ball_possession.size
        possession_percentages = {f"Team {team}": (count / total_frames) * 100 for team, count in zip(unique, counts)}
        return possession_percentages

    def calculate_player_possession_time(self, tracks: Dict[str, List[Dict]], fps: int) -> pd.DataFrame:
        """
        Calculate the total possession time for each player in seconds.
        """
        possession_time = {}
        for frame in tracks["players"]:
            for player_id, player_data in frame.items():
                if player_data.get("has_ball", False):
                    possession_time[player_id] = possession_time.get(player_id, 0) + 1

        # Convert possession frames to seconds
        possession_time_seconds = {player_id: frames / fps for player_id, frames in possession_time.items()}

        # Convert to DataFrame
        possession_df = pd.DataFrame(list(possession_time_seconds.items()), columns=["Player ID", "Possession Time (s)"])
        return possession_df

    def calculate_player_speed(self, tracks: Dict[str, List[Dict]], fps: int, video_resolution: tuple) -> pd.DataFrame:
        """
        Calculate the average speed of each player in meters per second (m/s) and kilometers per hour (km/h),
        using FIFA standard field dimensions.
        """
        # FIFA standard field dimensions
        field_length_m = 105  # in meters
        field_width_m = 68    # in meters

        # Video resolution (width, height) in pixels
        video_width_px, video_height_px = video_resolution

        # Calculate pixels per meter
        pixels_per_meter_length = video_width_px / field_length_m
        pixels_per_meter_width = video_height_px / field_width_m
        pixels_per_meter = (pixels_per_meter_length + pixels_per_meter_width) / 2  # Average scale

        # Calculate player speed
        speed_data = {}
        for frame_num in range(1, len(tracks["players"])):
            for player_id, player_data in tracks["players"][frame_num].items():
                if player_id in tracks["players"][frame_num - 1]:
                    prev_position = tracks["players"][frame_num - 1][player_id]["position"]
                    curr_position = player_data["position"]
                    distance_px = np.linalg.norm(np.array(curr_position) - np.array(prev_position))
                    speed_data[player_id] = speed_data.get(player_id, 0) + distance_px

        # Convert speed from pixels per second to meters per second and kilometers per hour
        speed_df = pd.DataFrame(
            [
                {
                    "Player ID": player_id,
                    # "Average Speed (m/s)": (speed / (len(tracks["players"]) / fps)) / pixels_per_meter,
                    "Average Speed (km/h)": ((speed / (len(tracks["players"]) / fps)) / pixels_per_meter) * 3.6,
                }
                for player_id, speed in speed_data.items()
            ]
        )
        return speed_df

    def calculate_team_possession_time(self, ball_possession: np.ndarray, fps: int) -> Dict[str, float]:
        """
        Calculate the total possession time for each team in seconds.
        """
        unique, counts = np.unique(ball_possession, return_counts=True)
        possession_time = {f"Team {team}": count / fps for team, count in zip(unique, counts)}
        return possession_time

    def generate_heatmap(self, tracks: Dict[str, List[Dict]], output_path: str, team_filter: int = None) -> None:
        """
        Generate a heatmap of player movements. Optionally filter by team.
        """
        positions = []
        for frame in tracks["players"]:
            for player_data in frame.values():
                if team_filter is None or player_data["team"] == team_filter:
                    positions.append(player_data["position"])

        positions = np.array(positions)
        heatmap, xedges, yedges = np.histogram2d(positions[:, 0], positions[:, 1], bins=50)

        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap.T, cmap="viridis", cbar=True)
        plt.title(f"Player Movement Heatmap{' (Team ' + str(team_filter) + ')' if team_filter else ''}")
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.savefig(output_path)
        plt.close()

    def save_insights(self, ball_possession: Dict[str, float], player_possession: pd.DataFrame, player_speed: pd.DataFrame, team_possession: Dict[str, int]) -> None:
        """
        Save insights to CSV and JSON files.
        """
        # Convert team_possession values to int
        team_possession = {key: int(value) for key, value in team_possession.items()}

        # Save ball possession
        ball_possession_path = os.path.join(self.output_dir, "ball_possession.json")
        with open(ball_possession_path, "w") as f:
            import json
            json.dump(ball_possession, f, indent=4)

        # Save player possession
        player_possession_path = os.path.join(self.output_dir, "player_possession.csv")
        player_possession.to_csv(player_possession_path, index=False)

        # Save player speed
        player_speed_path = os.path.join(self.output_dir, "player_speed.csv")
        player_speed.to_csv(player_speed_path, index=False)

        # Save team possession
        team_possession_path = os.path.join(self.output_dir, "team_possession.json")
        with open(team_possession_path, "w") as f:
            json.dump(team_possession, f, indent=4)

    def generate_all_insights(self, tracks: Dict[str, List[Dict]], ball_possession: np.ndarray, fps: int) -> None:
        """
        Generate and save all insights.
        """
        ball_possession_data = self.calculate_ball_possession(ball_possession)
        player_possession_data = self.calculate_player_possession_time(tracks, fps)
        player_speed_data = self.calculate_player_speed(tracks, fps, video_resolution=(1920, 1080))
        team_possession_data = self.calculate_team_possession_time(ball_possession, fps)

        # Generate heatmaps
        heatmap_path = os.path.join(self.output_dir, "player_heatmap.png")
        self.generate_heatmap(tracks, heatmap_path)

        team1_heatmap_path = os.path.join(self.output_dir, "team1_heatmap.png")
        self.generate_heatmap(tracks, team1_heatmap_path, team_filter=1)

        team2_heatmap_path = os.path.join(self.output_dir, "team2_heatmap.png")
        self.generate_heatmap(tracks, team2_heatmap_path, team_filter=2)

        # Save insights
        self.save_insights(ball_possession_data, player_possession_data, player_speed_data, team_possession_data)