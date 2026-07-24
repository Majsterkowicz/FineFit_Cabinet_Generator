from src import config
from src.core.prompt import ask_number, banner, choose, confirm_save
from src.services.cabinet_service import CabinetService
from src.services.id_generator import IdGenerator


class CabinetWizard:

    def __init__(self, project, section):

        self.project = project
        self.section = section

    def run(self):

        banner("Dodawanie szafki")

        if self.section.cabinets:
            print("Istniejące szafki:\n")
            for cabinet in self.section.cabinets:
                print(
                    f"{cabinet.cabinet_label}. "
                    f"{cabinet.cabinet_type}   "
                    f"{cabinet.width}x{cabinet.height}x{cabinet.depth}"
                )
        else:
            print("Sekcja nie zawiera jeszcze szafek.")

        print()
        print("-" * 42)
        print()

        cabinet_label = IdGenerator.generate_cabinet_label(self.section)

        print(f"Tworzona szafka nr: {cabinet_label}")
        print()

        cabinet_type = choose(
            list(config.CABINET_TYPES),
            label=lambda name: name,
            title="Typ szafki",
            back="Anuluj"
        )

        if cabinet_type is None:
            return None

        defaults = config.CABINET_TYPES[cabinet_type]

        print()
        print("ENTER - przyjmij wartość domyślną")
        print()

        width = ask_number("Szerokość [mm]", defaults["width"])
        height = ask_number("Wysokość  [mm]", defaults["height"])
        depth = ask_number("Głębokość [mm]", defaults["depth"])
        shelves = ask_number(
            "Liczba półek ", defaults["shelves"], minimum=0)
        fronts = ask_number(
            "Liczba frontów", defaults["fronts"], minimum=0)

        try:
            cabinet = CabinetService.create(
                project=self.project,
                section=self.section,
                cabinet_type=cabinet_type,
                width=width,
                height=height,
                depth=depth,
                shelves=shelves,
                fronts=fronts
            )

        except ValueError as error:
            print()
            print(f"Nie można wygenerować formatek: {error}")
            print("\nDodawanie szafki anulowano.")
            return None

        pieces = sum(part.quantity for part in cabinet.parts)

        banner("Podsumowanie")

        print(f"Numer szafki : {cabinet.cabinet_label}")
        print(f"Typ          : {cabinet.cabinet_type}")
        print(f"Wymiary      : {width} x {height} x {depth}")
        print(f"Półki        : {shelves}")
        print(f"Fronty       : {fronts}")
        print(f"Formatki     : {pieces} szt.")
        print()
        print("=" * 42)
        print()

        if not confirm_save():
            print("\nDodawanie szafki anulowano.")
            return None

        return cabinet
