from src import config
from src.models.part import Part
from src.services.id_generator import IdGenerator


class PartGenerator:
    """
    Generator elementów produkcyjnych (formatek) szafki.

    Konstrukcja korpusu:

    - boki na całej wysokości szafki,
    - wieńce wpuszczone pomiędzy boki,
    - półki cofnięte od frontu,
    - plecy HDF nakładane na tył korpusu,
    - fronty nakładane na korpus.

    Generator nie zapisuje projektu i nie komunikuje się
    z użytkownikiem.
    """

    @staticmethod
    def generate(project, cabinet) -> list[Part]:
        """Zwraca kompletną listę formatek dla szafki."""

        PartGenerator.validate(cabinet)

        parts = PartGenerator._specifications(cabinet)

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
    def _specifications(cabinet) -> list[Part]:
        """Formatki szafki w kolejności technologicznej, jeszcze bez ID."""

        return (
            PartGenerator._body(cabinet)
            + PartGenerator._shelves(cabinet)
            + PartGenerator._back(cabinet)
            + PartGenerator._fronts(cabinet)
        )

    @staticmethod
    def validate(cabinet):
        """Sprawdza, czy z podanych wymiarów da się zbudować korpus."""

        thickness = config.BOARD_THICKNESS

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

        if cabinet.shelves and cabinet.depth <= config.SHELF_SETBACK:
            raise ValueError(
                "Głębokość szafki jest za mała, aby cofnąć półkę od frontu."
            )

    @staticmethod
    def inner_width(cabinet) -> int:
        """Szerokość w świetle korpusu."""

        return cabinet.width - 2 * config.BOARD_THICKNESS

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
    def _body(cabinet) -> list[Part]:

        return [
            PartGenerator._part(
                "Bok", "bok",
                cabinet.height, cabinet.depth,
                config.BOARD_THICKNESS, 2, config.BOARD_MATERIAL,
                edge_length_1=config.EDGE_THICKNESS
            ),
            PartGenerator._part(
                "Wieniec", "wieniec",
                PartGenerator.inner_width(cabinet), cabinet.depth,
                config.BOARD_THICKNESS, 2, config.BOARD_MATERIAL,
                edge_length_1=config.EDGE_THICKNESS
            )
        ]

    @staticmethod
    def _shelves(cabinet) -> list[Part]:

        if not cabinet.shelves:
            return []

        return [
            PartGenerator._part(
                "Półka", "polka",
                PartGenerator.inner_width(cabinet),
                cabinet.depth - config.SHELF_SETBACK,
                config.BOARD_THICKNESS, cabinet.shelves,
                config.BOARD_MATERIAL,
                edge_length_1=config.EDGE_THICKNESS
            )
        ]

    @staticmethod
    def _back(cabinet) -> list[Part]:

        return [
            PartGenerator._part(
                "Plecy", "plecy",
                cabinet.height, cabinet.width,
                config.BACK_THICKNESS, 1, config.BACK_MATERIAL
            )
        ]

    @staticmethod
    def _fronts(cabinet) -> list[Part]:

        if not cabinet.fronts:
            return []

        gaps = (cabinet.fronts - 1) * config.FRONT_GAP

        front_width = round((cabinet.width - gaps) / cabinet.fronts, 1)

        edge = config.EDGE_THICKNESS

        return [
            PartGenerator._part(
                "Front", "front",
                cabinet.height, front_width,
                config.BOARD_THICKNESS, cabinet.fronts,
                config.FRONT_MATERIAL,
                edge_length_1=edge, edge_length_2=edge,
                edge_width_1=edge, edge_width_2=edge
            )
        ]
