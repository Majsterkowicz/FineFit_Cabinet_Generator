from src import config
from src.generators.bom_generator import BomGenerator


class PricingEngine:
    """
    Orientacyjna wycena projektu na podstawie zestawienia materiałowego.

    Wylicza koszt z gotowego modelu (jak pozostałe generatory), nie
    modyfikuje projektu. Ceny pochodzą z konfiguracji, więc są w jednym
    miejscu i łatwe do dostosowania.

    Pozycje kosztowe:
    - materiał: powierzchnia (m²) danego materiału x cena za m²,
    - obrzeże:  długość (m) x cena za metr,
    - okucia:   zawiasy i uchwyty wyliczone z liczby frontów.
    """

    @staticmethod
    def estimate(project, section_id: str = None) -> dict:

        parts = BomGenerator.collect_parts(project, section_id)
        summary = BomGenerator.summary(parts)

        materials = PricingEngine._material_lines(summary["materials"])
        edging = PricingEngine._edging_line(summary["edging_length"])
        hardware = PricingEngine._hardware_lines(parts)

        total = round(
            sum(line["cost"] for line in materials)
            + edging["cost"]
            + sum(line["cost"] for line in hardware),
            2
        )

        return {
            "currency": config.CURRENCY,
            "materials": materials,
            "edging": edging,
            "hardware": hardware,
            "total": total,
        }

    @staticmethod
    def _material_lines(material_summary) -> list:

        lines = []

        for entry in material_summary:

            unit_price = config.MATERIAL_PRICES.get(entry["material"], 0.0)

            lines.append({
                "material": entry["material"],
                "area": entry["area"],
                "unit_price": unit_price,
                "cost": round(entry["area"] * unit_price, 2),
            })

        return lines

    @staticmethod
    def _edging_line(length) -> dict:

        return {
            "length": length,
            "unit_price": config.EDGING_PRICE,
            "cost": round(length * config.EDGING_PRICE, 2),
        }

    @staticmethod
    def _hardware_lines(parts) -> list:

        fronts = sum(
            part.quantity for part in parts if part.part_type == "front"
        )

        items = [
            ("Zawiasy", fronts * config.HINGES_PER_FRONT, "hinge"),
            ("Uchwyty", fronts, "handle"),
        ]

        return [
            {
                "name": name,
                "quantity": quantity,
                "unit_price": config.HARDWARE_PRICES[key],
                "cost": round(quantity * config.HARDWARE_PRICES[key], 2),
            }
            for name, quantity, key in items
        ]
