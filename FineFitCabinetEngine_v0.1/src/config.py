import os

PROJECT_PREFIX = "P"

PROJECT_DIGITS = 3

# Ścieżka względna liczona jest od katalogu głównego projektu.
# Zmienna FINEFIT_PROJECTS_DIR pozwala wskazać inny katalog.

PROJECTS_DIRECTORY = os.environ.get("FINEFIT_PROJECTS_DIR", "projects")

# Konstrukcja korpusu.
# Jedno źródło prawdy - interfejsy otrzymują ten słownik przez /api/config.

CONSTRUCTION = {
    "board_thickness": 18,
    "back_thickness": 3,
    "shelf_setback": 20,
    "front_gap": 3,
    "edge_thickness": 2
}

BOARD_THICKNESS = CONSTRUCTION["board_thickness"]
BACK_THICKNESS = CONSTRUCTION["back_thickness"]
SHELF_SETBACK = CONSTRUCTION["shelf_setback"]
FRONT_GAP = CONSTRUCTION["front_gap"]
EDGE_THICKNESS = CONSTRUCTION["edge_thickness"]

# Typy szafek oraz wymiary domyślne

CABINET_TYPES = {
    "dolna": {
        "width": 600, "height": 720, "depth": 560, "shelves": 1, "fronts": 2
    },
    "gorna": {
        "width": 600, "height": 720, "depth": 300, "shelves": 2, "fronts": 2
    },
    "slupek": {
        "width": 600, "height": 2000, "depth": 560, "shelves": 4, "fronts": 2
    },
    "inna": {
        "width": 600, "height": 720, "depth": 560, "shelves": 1, "fronts": 1
    }
}

# Materiały

BOARD_MATERIAL = "Płyta 18mm"

BACK_MATERIAL = "HDF 3mm"

FRONT_MATERIAL = "Front 18mm"