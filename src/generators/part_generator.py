from src.models.part import Part
from src.services.id_generator import IdGenerator
from src.services.settings_manager import current_settings


class PartGenerator:
    """
    Generator elementów produkcyjnych (formatek) szafki.

    Konstrukcja korpusu:

    - boki na całej wysokości szafki,
    - wieńce wpuszczone pomiędzy boki,
    - półki cofnięte od frontu,
    - plecy HDF nakładane na tył korpusu,
    - fronty nakładane na korpus.

    Wymiary konstrukcyjne i nazwy materiałów pochodzą z ustawień globalnych.
    Generator nie zapisuje projektu i nie komunikuje się z użytkownikiem.
    """

    @staticmethod
    def generate(project, cabinet, settings=None) -> list[Part]:
        """
        Zwraca kompletną listę formatek dla szafki.

        settings można podać, aby uniknąć powtórnego odczytu w obrębie
        jednej operacji (np. CabinetService); bez nich czytamy raz tutaj.
        """

        if settings is None:
            settings = current_settings()

        PartGenerator.validate(cabinet, settings)

        parts = PartGenerator._specifications(cabinet, settings)

        # numerację całej serii wyznaczamy jednym przebiegiem
        first_number = IdGenerator.next_part_number(project)

        for index, part in enumerate(parts, start=1):

            part.part_id = IdGenerator.format_part_id(
                project,
                first_number + index - 1
            )

            part.part_label = IdGenerator.generate_part_label(cabinet, index)

        return parts

    @staticmethod
    def _specifications(cabinet, settings) -> list[Part]:
        """Formatki szafki w kolejności technologicznej, jeszcze bez ID."""

        return (
            PartGenerator._body(cabinet, settings)
            + PartGenerator._shelves(cabinet, settings)
            + PartGenerator._back(cabinet, settings)
            + PartGenerator._fronts(cabinet, settings)
        )

    @staticmethod
    def validate(cabinet, settings):
        """Sprawdza, czy z podanych wymiarów da się zbudować korpus."""

        thickness = settings["construction"]["board_thickness"]

        if cabinet.width <= 2 * thickness:
            raise ValueError(
                "Szerokość szafki musi być większa niż grubość dwóch boków."
            )

        if cabinet.height <= 2 * thickness:
            raise ValueError(
                "Wysokość szafki musi być większa niż grubość dwóch wieńców."
            )

        if cabinet.depth <= 0:
            raise ValueError("Głębokość szafki musi być większa od zera.")

        if cabinet.shelves < 0:
            raise ValueError("Liczba półek nie może być ujemna.")

        if cabinet.fronts < 0:
            raise ValueError("Liczba frontów nie może być ujemna.")

        setback = settings["construction"]["shelf_setback"]

        if cabinet.shelves and cabinet.depth <= setback:
            raise ValueError(
                "Głębokość szafki jest za mała, aby cofnąć półkę od frontu."
            )

    @staticmethod
    def inner_width(cabinet, settings) -> int:
        """Szerokość w świetle korpusu."""

        return cabinet.width - 2 * settings["construction"]["board_thickness"]

    @staticmethod
    def _part(part_name, part_type, length, width, thickness,
              quantity, material, **edges) -> Part:
        """Formatka bez numeracji - ID nadaje generate()."""

        return Part(
            part_id="",
            part_label="",
            part_name=part_name,
            part_type=part_type,
            length=length,
            width=width,
            thickness=thickness,
            quantity=quantity,
            material=material,
            **edges
        )

    @staticmethod
    def _body(cabinet, settings) -> list[Part]:

        board_thickness = settings["construction"]["board_thickness"]
        edge = settings["construction"]["edge_thickness"]
        board = settings["materials"]["board"]["name"]

        return [
            PartGenerator._part(
                "Bok", "bok",
                cabinet.height, cabinet.depth,
                board_thickness, 2, board,
                edge_length_1=edge
            ),
            PartGenerator._part(
                "Wieniec", "wieniec",
                PartGenerator.inner_width(cabinet, settings), cabinet.depth,
                board_thickness, 2, board,
                edge_length_1=edge
            )
        ]

    @staticmethod
    def _shelves(cabinet, settings) -> list[Part]:

        if not cabinet.shelves:
            return []

        construction = settings["construction"]
        board = settings["materials"]["board"]["name"]

        return [
            PartGenerator._part(
                "Półka", "polka",
                PartGenerator.inner_width(cabinet, settings),
                cabinet.depth - construction["shelf_setback"],
                construction["board_thickness"], cabinet.shelves,
                board,
                edge_length_1=construction["edge_thickness"]
            )
        ]

    @staticmethod
    def _back(cabinet, settings) -> list[Part]:

        return [
            PartGenerator._part(
                "Plecy", "plecy",
                cabinet.height, cabinet.width,
                settings["construction"]["back_thickness"], 1,
                settings["materials"]["back"]["name"]
            )
        ]

    @staticmethod
    def _fronts(cabinet, settings) -> list[Part]:

        if not cabinet.fronts:
            return []

        construction = settings["construction"]
        edge = construction["edge_thickness"]

        gaps = (cabinet.fronts - 1) * construction["front_gap"]

        front_width = round((cabinet.width - gaps) / cabinet.fronts, 1)

        return [
            PartGenerator._part(
                "Front", "front",
                cabinet.height, front_width,
                construction["board_thickness"], cabinet.fronts,
                settings["materials"]["front"]["name"],
                edge_length_1=edge, edge_length_2=edge,
                edge_width_1=edge, edge_width_2=edge
            )
        ]
