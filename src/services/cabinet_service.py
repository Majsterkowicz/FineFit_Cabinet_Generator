from src.generators.part_generator import PartGenerator
from src.models.cabinet import Cabinet
from src.services.id_generator import IdGenerator
from src.services.settings_manager import current_settings


class CabinetService:
    """
    Logika biznesowa szafek.

    Usługa tworzy szafkę wraz z kompletem formatek.
    Nie komunikuje się z użytkownikiem i nie zapisuje projektu.
    """

    @staticmethod
    def create(
            project,
            section,
            cabinet_type: str,
            width: int,
            height: int,
            depth: int,
            shelves: int,
            fronts: int):
        """Tworzy szafkę i generuje jej elementy produkcyjne."""

        # Jeden odczyt ustawień na całą operację (walidacja + generowanie).
        settings = current_settings()

        CabinetService.validate_type(cabinet_type, settings)

        cabinet = Cabinet(
            cabinet_id=IdGenerator.generate_cabinet_id(project),
            cabinet_label=IdGenerator.generate_cabinet_label(section),
            cabinet_type=cabinet_type,
            width=width,
            height=height,
            depth=depth,
            shelves=shelves,
            fronts=fronts
        )

        cabinet.parts = PartGenerator.generate(project, cabinet, settings)

        return cabinet

    @staticmethod
    def update(
            project,
            cabinet,
            cabinet_type: str,
            width: int,
            height: int,
            depth: int,
            shelves: int,
            fronts: int):
        """
        Zmienia wymiary szafki i generuje formatki od nowa.

        Nowe formatki otrzymują nowe ID systemowe.
        Stare ID nie są ponownie wykorzystywane.
        """

        settings = current_settings()

        CabinetService.validate_type(cabinet_type, settings)

        cabinet.cabinet_type = cabinet_type
        cabinet.width = width
        cabinet.height = height
        cabinet.depth = depth
        cabinet.shelves = shelves
        cabinet.fronts = fronts

        cabinet.parts = PartGenerator.generate(project, cabinet, settings)

        return cabinet

    @staticmethod
    def find(section, cabinet_id: str):
        """Zwraca szafkę o podanym ID systemowym."""

        for cabinet in section.cabinets:
            if cabinet.cabinet_id == cabinet_id:
                return cabinet

        raise LookupError(f"Nie znaleziono szafki {cabinet_id}.")

    @staticmethod
    def delete(project, section, cabinet_id: str):
        """Usuwa szafkę i przelicza numerację technologiczną."""

        cabinet = CabinetService.find(section, cabinet_id)

        section.cabinets.remove(cabinet)

        IdGenerator.renumber_project(project)

        return cabinet

    @staticmethod
    def validate_type(cabinet_type: str, settings):

        cabinet_types = settings["cabinet_types"]

        if cabinet_type not in cabinet_types:

            available = ", ".join(cabinet_types)

            raise ValueError(
                f"Nieznany typ szafki: {cabinet_type}. "
                f"Dostępne typy: {available}."
            )
