from src.generators.bom_generator import BomGenerator


class PricingEngine:
    """
    Orientacyjna wycena projektu na podstawie zestawienia materiałowego.

    Wylicza koszt z gotowego modelu (jak pozostałe generatory), nie
    modyfikuje projektu. Ceny pochodzą z migawki cennika projektu
    (project.pricing), więc wycena jest stabilna niezależnie od zmian
    ustawień globalnych.

    Pozycje kosztowe:
    - materiał: powierzchnia (m²) danego materiału x cena za m²,
    - obrzeże:  długość (m) x cena za metr,
    - okucia:   zawiasy i uchwyty wyliczone z liczby frontów.
    """

    @staticmethod
    def snapshot(settings: dict) -> dict:
        """
        Migawka cennika dla nowego projektu (kopiowana do project.json).

        Późniejsza zmiana ustawień globalnych nie zmienia istniejących
        wycen. Ceny materiałów kluczujemy nazwą materiału - tak samo jak
        formatki - dzięki czemu wycena nie wymaga mapowania rola->nazwa.
        Producent migawki mieszka razem z konsumentem (estimate).
        """

        return {
            "currency": settings["currency"],
            "material_prices": {
                material["name"]: material["price"]
                for material in settings["materials"].values()
            },
            "edging_price": settings["edging_price"],
            "hinges_per_front": settings["hardware"]["hinges_per_front"],
            "hardware_prices": {
                "hinge": settings["hardware"]["hinge_price"],
                "handle": settings["hardware"]["handle_price"],
            },
        }

    @staticmethod
    def estimate(project, section_id: str = None) -> dict:

        pricing = project.pricing

        parts = BomGenerator.collect_parts(project, section_id)
        summary = BomGenerator.summary(parts)

        materials = PricingEngine._material_lines(
            summary["materials"], pricing)
        edging = PricingEngine._edging_line(
            summary["edging_length"], pricing)
        hardware = PricingEngine._hardware_lines(parts, pricing)

        total = round(
            sum(line["cost"] for line in materials)
            + edging["cost"]
            + sum(line["cost"] for line in hardware),
            2
        )

        return {
            "currency": pricing["currency"],
            "materials": materials,
            "edging": edging,
            "hardware": hardware,
            "total": total,
        }

    @staticmethod
    def _material_lines(material_summary, pricing) -> list:

        prices = pricing["material_prices"]

        lines = []

        for entry in material_summary:

            unit_price = prices.get(entry["material"], 0.0)

            lines.append({
                "material": entry["material"],
                "area": entry["area"],
                "unit_price": unit_price,
                "cost": round(entry["area"] * unit_price, 2),
            })

        return lines

    @staticmethod
    def _edging_line(length, pricing) -> dict:

        unit_price = pricing["edging_price"]

        return {
            "length": length,
            "unit_price": unit_price,
            "cost": round(length * unit_price, 2),
        }

    @staticmethod
    def _hardware_lines(parts, pricing) -> list:

        fronts = sum(
            part.quantity for part in parts if part.part_type == "front"
        )

        prices = pricing["hardware_prices"]

        items = [
            ("Zawiasy", fronts * pricing["hinges_per_front"], "hinge"),
            ("Uchwyty", fronts, "handle"),
        ]

        return [
            {
                "name": name,
                "quantity": quantity,
                "unit_price": prices[key],
                "cost": round(quantity * prices[key], 2),
            }
            for name, quantity, key in items
        ]
