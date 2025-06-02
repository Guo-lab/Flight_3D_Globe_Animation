import json
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from globe import FlightGlobeAnimator
from utils import *

flights_data = load_flight_information("flights.json")

if __name__ == "__main__":
    print("Creating smooth flight animation...")

    animator = FlightGlobeAnimator(
        flights_data,
        great_circle_path,
        config={"total_frames": 400, "points_per_flight": 150},
        verbose=True,
    )
    fig = animator.create_animation()
    fig.show()

    fig.write_html("smooth_flight_animation.html")
    print("✓ Animation saved as 'smooth_flight_animation.html'")
    print("Click 'Play Journey' to start the animation!")
