# ============================================
# ===== Vehicles Visualization Constants =====
# ============================================
DEFAULT_VEHICLE_STYLES = {
    "plane": {"color": "#FF6B6B", "icon": "✈️"},
    "train": {"color": "#4ECDC4", "icon": "🚄"},
    "car": {"color": "#45B7D1", "icon": "🚗"},
    "socket": {"color": "#F7B7A3", "icon": "🚀"},
    "ship": {"color": "#FFB400", "icon": "🚢"},
    "default": {"color": "#FFA726", "icon": "📍"},
}

DEFAULT_VEHICLE_COLOR = "#FFA726"


# ==========================================
# ===== Flight Visualization Constants =====
# ==========================================
DEFAULT_TOTAL_FRAMES = 200
DEFAULT_POINTS_PER_FLIGHT = 50

DEFAULT_GEO_LAYOUT = {
    "projection_type": "orthographic",
    # "projection_type": "mercator",
    "showland": True,
    "landcolor": "rgb(40, 40, 40)",
    "showocean": True,
    "oceancolor": "rgb(0, 20, 40)",
    "showlakes": True,
    "lakecolor": "rgb(0, 20, 40)",
    "showrivers": True,
    "rivercolor": "rgb(0, 20, 40)",
    "showcoastlines": True,
    "coastlinecolor": "rgb(100, 100, 100)",
    "bgcolor": "black",
    "showframe": True,
    "projection_rotation": {"lon": 0, "lat": 20, "roll": 0},
}

DEFAULT_FIG_WIDTH = 1400
DEFAULT_FIG_HEIGHT = 900


# ==============================
# ========= TEXT STYLES ========
# ==============================
DEFAULT_TITLE = {
    "text": "✈️ World Travel Journey Animation",
    "x": 0.5,
    "font": {"size": 24, "color": "white"},
}
DEFAULT_FONT = {"color": "white"}
DEFAULT_PAPER_BGCOLOR = "black"


# ==============================
# ===== ANIMATION CONTROLS =====
# ==============================
DEFAULT_PLAY_BUTTON = {
    "label": "▶️ Play Journey",
    "method": "animate",
    "args": [
        None,
        {
            "frame": {"duration": 40, "redraw": True},
            "fromcurrent": True,
            "transition": {"duration": 10},
        },
    ],
}

DEFAULT_PAUSE_BUTTON = {
    "label": "⏸️ Pause",
    "method": "animate",
    "args": [
        [None],
        {
            "frame": {"duration": 0, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 0},
        },
    ],
}

DEFAULT_RESTART_BUTTON = {
    "label": "🔄 Restart",
    "method": "animate",
    "args": [
        ["frame_0"],
        {
            "frame": {"duration": 0, "redraw": True},
            "mode": "immediate",
            "transition": {"duration": 0},
        },
    ],
}

DEFAULT_UPDATE_MENUS = [
    {
        "type": "buttons",
        "showactive": False,
        "x": 0.01,
        "y": 0.98,
        "xanchor": "left",
        "yanchor": "top",
        "buttons": [
            DEFAULT_PLAY_BUTTON,
            DEFAULT_PAUSE_BUTTON,
            DEFAULT_RESTART_BUTTON,
        ],
    }
]
