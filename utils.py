import json
from typing import Tuple

import numpy as np


def load_flight_information(json_path: str) -> dict:
    """
    Load flight information from a JSON file.

    Args:
        json_path (str): The path to the JSON file containing flight information.

    Returns:
        dict: A dictionary containing flight information.
    """
    with open(json_path, "r", encoding="utf-8") as file:
        flights_info = json.load(file)

    return flights_info


def great_circle_path(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    num_points: int = 50,
    type: str = "shortest",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate points along a great circle path between two coordinates
    using the spherical law of cosines.
    Calculate the great circle path between two points on the Earth
    and interpolate points along it.

    Args:
        lat1 (float): Latitude of start point in degrees.
        lon1 (float): Longitude of start point in degrees.
        lat2 (float): Latitude of end point in degrees.
        lon2 (float): Longitude of end point in degrees.
        num_points (int): Number of points along path (default: 50).
        type (str): Type of path to generate.
            The shortest route on a sphere like a flight path.

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            Arrays of latitudes and longitudes along the path.

    Raises:
        ValueError: If num_points < 2 or points are invalid
        (e.g., identical or antipodal).
    """

    if num_points < 2:
        raise ValueError("num_points must be at least 2")
    s, c = np.sin, np.cos

    # Convert to radians
    rlat1, rlon1, rlat2, rlon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Compute angular distance
    cd = s(rlat1) * s(rlat2) + c(rlat1) * c(rlat2) * c(rlon2 - rlon1)
    angular_distance = np.arccos(np.clip(cd, -1.0, 1.0))

    # Handle edge cases
    if abs(angular_distance) < 1e-10:
        return np.full(num_points, lat1), np.full(num_points, lon1)
    if abs(angular_distance - np.pi) < 1e-10:
        raise ValueError("Antipodal points have ambiguous great circle path")

    fraction = np.linspace(0, 1, num_points)
    a = np.sin((1 - fraction) * angular_distance) / np.sin(angular_distance)
    b = np.sin(fraction * angular_distance) / np.sin(angular_distance)

    # Cartesian coordinates
    x = a[:, None] * c(rlat1) * c(rlon1) + b[:, None] * c(rlat2) * c(rlon2)
    y = a[:, None] * c(rlat1) * s(rlon1) + b[:, None] * c(rlat2) * s(rlon2)
    z = a[:, None] * s(rlat1) + b[:, None] * s(rlat2)

    # Convert back to lat/lon
    lats = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))
    lons = np.degrees(np.arctan2(y, x))
    return lats.flatten(), lons.flatten()


import random


def random_named_color():
    palette = [
        "#FF6B6B",  # coral
        "#4ECDC4",  # turquoise
        "#556270",  # dark blue-gray
        "#C7F464",  # lime
        "#FFA726",  # amber
        "#66BB6A",  # green
        "#29B6F6",  # sky blue
        "#AB47BC",  # purple
    ]
    return random.choice(palette)
