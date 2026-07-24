class BomGenerator:
    """
    Zestawienie materiałowe projektu.

    Łączy identyczne formatki z całego projektu w jedną pozycję
    listy rozkroju.
    """

    @staticmethod
    def collect_parts(project, section_id: str = None) -> list:
        """Zwraca wszystkie formatki projektu lub wybranej sekcji."""

        parts = []

        for section in project.sections:

            if section_id and section.section_id != section_id:
                continue

            for cabinet in section.cabinets:
                parts.extend(cabinet.parts)

        return parts

    @staticmethod
    def part_area(part) -> float:
        """Powierzchnia formatek danej pozycji w metrach kwadratowych."""

        return part.length * part.width * part.quantity / 1_000_000

    @staticmethod
    def edging_length(part) -> float:
        """Długość obrzeża pozycji w milimetrach."""

        return part.quantity * (
            part.length * (
                bool(part.edge_length_1) + bool(part.edge_length_2)
            )
            + part.width * (
                bool(part.edge_width_1) + bool(part.edge_width_2)
            )
        )

    @staticmethod
    def cutting_list(parts) -> list:
        """
        Lista rozkroju pogrupowana po materiale i wymiarze.

        Przyjmuje gotową listę formatek, aby nie przechodzić
        drzewa projektu po raz drugi.
        """

        grouped = {}

        for part in parts:

            key = (
                part.material,
                part.part_name,
                part.length,
                part.width,
                part.thickness
            )

            row = grouped.setdefault(key, {
                "material": part.material,
                "part_name": part.part_name,
                "part_type": part.part_type,
                "length": part.length,
                "width": part.width,
                "thickness": part.thickness,
                "quantity": 0,
                "area": 0.0
            })

            row["quantity"] += part.quantity
            row["area"] += BomGenerator.part_area(part)

        for row in grouped.values():
            row["area"] = round(row["area"], 3)

        return sorted(
            grouped.values(),
            key=lambda row: (row["material"], -row["length"], -row["width"])
        )

    @staticmethod
    def summary(parts) -> dict:
        """Podsumowanie zużycia materiału oraz oklejania krawędzi."""

        materials = {}
        total_parts = 0
        edging = 0.0

        for part in parts:

            entry = materials.setdefault(
                part.material,
                {"material": part.material, "quantity": 0, "area": 0.0}
            )

            entry["quantity"] += part.quantity
            entry["area"] += BomGenerator.part_area(part)

            total_parts += part.quantity
            edging += BomGenerator.edging_length(part)

        for entry in materials.values():
            entry["area"] = round(entry["area"], 3)

        return {
            "materials": sorted(
                materials.values(),
                key=lambda entry: entry["material"]
            ),
            "total_parts": total_parts,
            "total_area": round(
                sum(entry["area"] for entry in materials.values()),
                3
            ),
            "edging_length": round(edging / 1000, 2)
        }
