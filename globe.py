import json
from datetime import datetime
from typing import Callable, Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go
from constants import (DEFAULT_FIG_HEIGHT, DEFAULT_FIG_WIDTH, DEFAULT_FONT,
                       DEFAULT_GEO_LAYOUT, DEFAULT_PAPER_BGCOLOR,
                       DEFAULT_POINTS_PER_FLIGHT, DEFAULT_TITLE,
                       DEFAULT_TOTAL_FRAMES, DEFAULT_UPDATE_MENUS,
                       DEFAULT_VEHICLE_COLOR, DEFAULT_VEHICLE_STYLES)
from utils import random_named_color


class FlightGlobeAnimator:
    """Creates an animated globe showing flight progression with Plotly."""

    def __init__(
        self,
        flights_data: List[Dict],
        great_circle_fn: Callable[
            [float, float, float, float, int], Tuple[np.ndarray, np.ndarray]
        ],
        config: Dict = None,
        verbose: bool = False,
    ):
        """
        Initialize animator with flights data and configuration.

        Args:
            flights_data: List of flight dictionaries with source, target, date, vehicle.
            great_circle_fn: Function to compute great circle paths (lat, lon arrays).
            config: Optional config for animation settings (e.g., frames, colors, etc,.).
        """

        self.flights = sorted(
            flights_data, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
        )
        self.flights_color = [random_named_color() for _ in self.flights]
        self.ending = False
        self.last_frame = None

        self.verbose = verbose
        if verbose:
            print()
            print("==" * 20)
            print(f"Loaded {len(self.flights)} flights for animation.")
            print(f"Date: {self.flights[0]['date']} to {self.flights[-1]['date']}")
            print(self.flights)
            print("--" * 20)
            print()

        self.great_circle_fn = great_circle_fn
        self.config = config or {}
        self._setup_config()

    def _setup_config(self) -> None:
        """Set up default configuration with overrides from provided config."""

        self.vehicle_styles = self.config.get("vehicle_styles", DEFAULT_VEHICLE_STYLES)
        self.total_frames = self.config.get("total_frames", DEFAULT_TOTAL_FRAMES)
        self.points_per_flight = self.config.get(
            "points_per_flight", DEFAULT_POINTS_PER_FLIGHT
        )
        self.geo_layout = self.config.get("geo_layout", DEFAULT_GEO_LAYOUT)

        self.frames_per_flight = max(1, self.total_frames // len(self.flights))
        output_log = f"Total frames: {self.total_frames}, "
        output_log += f"Frames per flight: {self.frames_per_flight}"

        if self.verbose:
            print(output_log)
            print("==" * 20)
            print()

        self.frame_data = []
        self.current_flight_idx = -1  # Track which flight we're currently on
        self.completed_flights = set()

    def _create_path_trace(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        vehicle: str,
        width: int,
        flight_idx: int,
    ) -> go.Scattergeo:
        """Create a Scattergeo trace for a flight path."""
        style = self.vehicle_styles.get(vehicle, {})

        lat_list = lats.tolist() if isinstance(lats, np.ndarray) else list(lats)
        lon_list = lons.tolist() if isinstance(lons, np.ndarray) else list(lons)

        return go.Scattergeo(
            lat=lat_list,
            lon=lon_list,
            mode="lines",
            line=dict(width=width, color=self.flights_color[flight_idx]),
            showlegend=True,
            text=f"{vehicle.title()} path",
            hoverinfo="skip",
            name=f"{vehicle.title()} path",
        )

    def _create_marker_trace(
        self, lat: float, lon: float, text: str, vehicle: str
    ) -> go.Scattergeo:
        """Create a Scattergeo trace for a marker (source or destination)."""

        style = self.vehicle_styles.get(vehicle, {})
        color = style.get("color", DEFAULT_VEHICLE_COLOR)

        return go.Scattergeo(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            marker=dict(
                size=12, color="white", line=dict(width=2, color=color), symbol="circle"
            ),
            text=[text],
            textposition="top center",
            textfont=dict(size=12, color="white"),
            showlegend=True,
            hoverinfo="text",
            hovertext=[f"City {text}"],
            name=f"City {text}",
        )

    def _create_moving_point_trace(
        self, lat: float, lon: float, vehicle: str
    ) -> go.Scattergeo:
        """Create a Scattergeo trace for the moving vehicle point."""

        style = self.vehicle_styles.get(vehicle, self.vehicle_styles["default"])
        return go.Scattergeo(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            marker=dict(size=15, color=style["color"], symbol="circle"),
            text=[style["icon"]],
            textposition="middle center",
            textfont=dict(size=20),
            showlegend=True,
            hoverinfo="text",
            hovertext=[f"Traveling by {vehicle}"],
            name=f"Moving By {vehicle}",
        )

    def _generate_frame(self, frame_idx: int) -> go.Frame:
        """Generate a single animation frame."""

        if self.ending:
            # If the animation has ended, return the last frame
            if self.last_frame is not None:
                return go.Frame(data=self.last_frame, name=f"frame_{frame_idx}")

        frame_data = []

        # Calculate which flight we're currently on
        current_flight_idx = min(
            frame_idx // self.frames_per_flight, len(self.flights) - 1
        )
        frame_within_flight = frame_idx % self.frames_per_flight + 1

        if self.verbose:
            print(
                f"Frame {frame_idx}: current_flight_idx={current_flight_idx}, \
Flight: {self.flights[current_flight_idx]['source']['city']} to {self.flights[current_flight_idx]['target']['city']}, \
frame_within_flight={frame_within_flight}"
            )

        # Show all completed flights
        for i in range(current_flight_idx):
            flight = self.flights[i]
            lats, lons = self.great_circle_fn(
                flight["source"]["lat"],
                flight["source"]["lng"],
                flight["target"]["lat"],
                flight["target"]["lng"],
                self.points_per_flight,
            )
            path_trace = self._create_path_trace(
                lats, lons, flight["vehicle"], width=2, flight_idx=i
            )
            frame_data.append(path_trace)

            # Add source and destination markers
            source_trace = self._create_marker_trace(
                flight["source"]["lat"],
                flight["source"]["lng"],
                flight["source"]["city"],
                flight["vehicle"],
            )
            dest_trace = self._create_marker_trace(
                flight["target"]["lat"],
                flight["target"]["lng"],
                flight["target"]["city"],
                flight["vehicle"],
            )
            frame_data.append(source_trace)
            frame_data.append(dest_trace)

            if self.verbose:
                print(
                    f"  Added completed flight {i}: {flight['source']['city']} to {flight['target']['city']}, {len(lats)} points"
                )
                pass

        # Show current flight in progress
        if current_flight_idx < len(self.flights):
            current_path = self.flights[current_flight_idx]

            lats, lons = self.great_circle_fn(
                current_path["source"]["lat"],
                current_path["source"]["lng"],
                current_path["target"]["lat"],
                current_path["target"]["lng"],
                self.points_per_flight,
            )
            # print(current_path)

            # Calculate how much of current flight to show
            progress = frame_within_flight / self.frames_per_flight
            progress = min(progress, 1.0)

            # Number of points to show in current path
            points_to_show = max(2, int(progress * len(lats)))
            partial_lats = lats[:points_to_show]
            partial_lons = lons[:points_to_show]
            if self.verbose:
                print(
                    f"  Current flight {current_flight_idx}: {current_path['source']['city']} to {current_path['target']['city']}, \
                        {points_to_show}/{len(lats)} points"
                )

            if len(partial_lats) > 1:
                path_trace = self._create_path_trace(
                    partial_lats,
                    partial_lons,
                    current_path["vehicle"],
                    width=7,
                    flight_idx=current_flight_idx,
                )
                frame_data.append(path_trace)

                if self.verbose:
                    print(f"  Added path trace: {points_to_show} points")

            # Add source marker for current flight
            source_trace = self._create_marker_trace(
                current_path["source"]["lat"],
                current_path["source"]["lng"],
                current_path["source"]["city"],
                current_path["vehicle"],
            )
            frame_data.append(source_trace)

            # Add moving point at current position
            if progress > 0 and len(partial_lats) > 0:
                current_lat = partial_lats[-1]
                current_lon = partial_lons[-1]

                moving_trace = self._create_moving_point_trace(
                    current_lat, current_lon, current_path["vehicle"]
                )
                frame_data.append(moving_trace)

                if self.verbose:
                    print(f"  Added moving point at ({current_lat}, {current_lon})")

            # Add destination marker when flight is complete
            if progress >= 1.0:
                dest_trace = self._create_marker_trace(
                    current_path["target"]["lat"],
                    current_path["target"]["lng"],
                    current_path["target"]["city"],
                    current_path["vehicle"],
                )
                frame_data.append(dest_trace)

                if self.verbose:
                    print(
                        f"  Added destination marker: {current_path['target']['city']}"
                    )

                if current_flight_idx == len(self.flights) - 1:
                    self.ending = True
                    self.last_frame = frame_data

        # print(len(frame_data))
        try:
            return go.Frame(data=frame_data, name=f"frame_{frame_idx}")

        except Exception as e:
            print(f"Error in frame {frame_idx}: {e}")
            return go.Frame(data=[], name=f"frame_{frame_idx}")

    def create_animation(self) -> go.Figure:
        """Create the animated globe figure."""

        frames = [self._generate_frame(i) for i in range(self.total_frames)]

        # for each_frame in frames:
        #     print(len(each_frame.data), each_frame.name)

        # print(frames[-2])
        # print(frames)
        print()

        export_data = []
        for i, frame in enumerate(frames):
            frame_info = {
                "frame_number": i,
                "frame_name": frame.name,
                "current_flight_idx": min(
                    i // self.frames_per_flight, len(self.flights) - 1
                ),
                "current_flight": f"{self.flights[min(i // self.frames_per_flight, len(self.flights) - 1)]['source']['city']} to {self.flights[min(i // self.frames_per_flight, len(self.flights) - 1)]['target']['city']}",
                "trace_count": len(frame.data),
                "traces": [],
            }

            for j, trace in enumerate(frame.data):
                # Safely access trace attributes
                mode = getattr(trace, "mode", "unknown")
                lat = getattr(trace, "lat", [])
                lon = getattr(trace, "lon", [])
                text = getattr(trace, "text", "N/A")
                name = getattr(trace, "name", "N/A")

                # Handle color (line.color for paths, marker.color for markers)
                color = "N/A"
                if hasattr(trace, "line") and hasattr(trace.line, "color"):
                    color = trace.line.color
                elif hasattr(trace, "marker") and hasattr(trace.marker, "color"):
                    color = trace.marker.color

                trace_info = {
                    "trace_index": j,
                    "type": type(trace).__name__,
                    "mode": mode,
                    "lat_count": len(lat),
                    "lon_count": len(lon),
                    "lat": list(lat) if lat else [],
                    "lon": list(lon) if lon else [],
                    "color": color,
                    "text": text if text != "N/A" else str(text),
                    "name": name,
                }
                frame_info["traces"].append(trace_info)
                export_data.append(frame_info)

        # Export to JSON file
        with open("frame_data_export.json", "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        print("Exported frame_data to 'frame_data_export.json'")

        if self.verbose:
            # for each_frame in frames:
            #     print(f"Frame {each_frame.name} has")
            #     for each_data in each_frame.data:
            #         print(each_data["text"], "with ", len(each_data["lat"]), "points.")
            pass

        # TODO: Normally the data should be set as initial data,
        # but Plotly seems not support this for different traces.
        # The temporary solution is to show all flights at first and
        # present the animation one by one.
        fig = go.Figure(data=frames[-1].data, frames=frames, skip_invalid=False)
        # self.geo_layout["projection_rotation"]= {"lon": mid_lon, "lat": mid_lat}

        fig.update_layout(
            title=DEFAULT_TITLE,
            geo=self.geo_layout,
            paper_bgcolor=DEFAULT_PAPER_BGCOLOR,
            font=DEFAULT_FONT,
            updatemenus=DEFAULT_UPDATE_MENUS,
            width=DEFAULT_FIG_WIDTH,
            height=DEFAULT_FIG_HEIGHT,
            sliders=[
                {
                    "steps": [
                        {
                            "args": [[f"frame_{i}"]],
                            "label": f"Frame {i}",
                            "method": "animate",
                        }
                        for i in range(self.total_frames + 1)
                    ],
                    "x": 0.1,
                    "len": 0.9,
                    "y": 0,
                    "yanchor": "top",
                }
            ],
        )
        return fig
