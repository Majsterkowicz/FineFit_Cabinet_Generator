import os

PROJECT_PREFIX = "P"

PROJECT_DIGITS = 3

# Ścieżka względna liczona jest od katalogu głównego projektu.
# Zmienna FINEFIT_PROJECTS_DIR pozwala wskazać inny katalog.

PROJECTS_DIRECTORY = os.environ.get("FINEFIT_PROJECTS_DIR", "projects")

SETTINGS_FILE = os.environ.get("FINEFIT_SETTINGS_FILE", "settings.json")

# Ustawienia domyślne.
#
# To jest jedyne źródło wartości fabrycznych. SettingsManager tworzy z nich
# settings.json przy pierwszym uruchomieniu; potem plik jest edytowalny w UI.
# Ceny konkretnego projektu to migawka tych ustawień z chwili utworzenia
# projektu (patrz Project.pricing).

DEFAULT_SETTINGS = {

    # Konstrukcja korpusu (mm).
    "construction": {
        "board_thickness": 18,
        "back_thickness": 3,
        "shelf_setback": 20,
        "front_gap": 3,
        "edge_thickness": 2,
    },

    # Materiały wg roli: nazwa (na formatkach) oraz cena za m².
    "materials": {
        "board": {"name": "Płyta 18mm", "price": 45.0},
        "back": {"name": "HDF 3mm", "price": 20.0},
        "front": {"name": "Front 18mm", "price": 90.0},
    },

    "edging_price": 3.0,          # cena za metr obrzeża

    "hardware": {
        "hinges_per_front": 2,
        "hinge_price": 8.0,       # cena za sztukę
        "handle_price": 12.0,     # cena za sztukę
    },

    "currency": "PLN",

    # Typy szafek oraz wymiary domyślne.
    "cabinet_types": {
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
        },
    },
}
