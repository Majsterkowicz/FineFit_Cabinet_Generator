import copy
import json
from pathlib import Path

from src import config
from src.services.storage import atomic_write_json


class SettingsManager:
    """
    Ustawienia globalne aplikacji (settings.json).

    Jedno źródło prawdy dla CLI i API. Przy braku pliku ustawienia
    pochodzą z config.DEFAULT_SETTINGS; brakujące klucze (np. dodane
    w nowej wersji) są uzupełniane wartościami domyślnymi przy odczycie.
    """

    def __init__(self, settings_path=None):

        if settings_path is None:

            root = Path(__file__).resolve().parents[2]

            settings_path = root / config.SETTINGS_FILE

        self.settings_path = Path(settings_path)

    def load(self) -> dict:

        if not self.settings_path.exists():
            return copy.deepcopy(config.DEFAULT_SETTINGS)

        with open(self.settings_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return self._with_defaults(data)

    def save(self, settings: dict) -> dict:
        """
        Zapisuje ustawienia (atomowo) i zwraca zapisaną wersję.

        Uzupełnia brakujące klucze, aby na dysku znalazł się komplet.
        """

        merged = self._with_defaults(settings)

        atomic_write_json(self.settings_path, merged)

        return merged

    @staticmethod
    def _with_defaults(data: dict) -> dict:
        """Domyślne ustawienia nadpisane wartościami z pliku (płytko na
        poziomie sekcji)."""

        merged = copy.deepcopy(config.DEFAULT_SETTINGS)

        for key, value in (data or {}).items():
            merged[key] = value

        return merged


# Domyślny menedżer oraz akcesor dla warstw, które nie wstrzykują ustawień.
# Ustawienia są małe, a generowanie formatek nie jest ścieżką gorącą, więc
# odczyt z dysku na żądanie jest wystarczający i zawsze aktualny.

settings_manager = SettingsManager()


def current_settings() -> dict:
    return settings_manager.load()
