from src import config
from src.core.cabinet_wizard import CabinetWizard
from src.core.prompt import ask_cabinet_dimensions, choose, confirm
from src.services.cabinet_service import CabinetService


class SectionWorkspace:

    def __init__(self, project, section, project_manager):

        self.project = project
        self.section = section
        self.project_manager = project_manager

    def run(self):

        actions = {
            "1": self.show_section_info,
            "2": self.show_cabinets,
            "3": self.add_cabinet,
            "4": self.edit_cabinet,
            "5": self.delete_cabinet,
            "6": self.show_parts,
        }

        while True:

            print("\n========================================")
            print(
                f"Sekcja {self.section.section_number} - "
                f"{self.section.section_name}"
            )
            print("========================================")

            print("1. Informacje o sekcji")
            print("2. Lista szafek")
            print("3. Dodaj szafkę")
            print("4. Edytuj szafkę")
            print("5. Usuń szafkę")
            print("6. Lista formatek")
            print("0. Powrót")

            choice = input("\nWybierz opcję: ")

            if choice == "0":
                break

            action = actions.get(choice)

            if action:
                action()
            else:
                print("\nNiepoprawny wybór.")

            # Pauza „ENTER - powrót” jest jedna, na poziomie pętli menu,
            # zamiast powtarzana w każdej gałęzi każdej akcji.
            input("\nENTER - powrót")

    def show_section_info(self):
        print("\n========================================")
        print("Informacje o sekcji")
        print("========================================")

        print(f"ID: {self.section.section_id}")
        print(f"Numer: {self.section.section_number}")
        print(f"Nazwa: {self.section.section_name}")
        print(f"Liczba szafek: {len(self.section.cabinets)}")

    def show_cabinets(self):
        print("\n========================================")
        print("Lista szafek")
        print("========================================")
        if not self.section.cabinets:
            print("\nBrak szafek.")
        else:
            for index, cabinet in enumerate(
                    self.section.cabinets,
                    start=1):
                print(
                    f"{index}. "
                    f"{cabinet.cabinet_label}   "
                    f"{cabinet.cabinet_type}"
                )

    def add_cabinet(self):

        wizard = CabinetWizard(self.project, self.section)

        cabinet = wizard.run()

        if cabinet is None:
            return

        self.section.add_cabinet(cabinet)

        self.project_manager.save_project(self.project)

        print()
        print("=" * 42)
        print(" Szafka została dodana")
        print("=" * 42)
        print()
        print(f"ID systemowe : {cabinet.cabinet_id}")
        print(f"Numer szafki : {cabinet.cabinet_label}")
        print(f"Formatki     : {len(cabinet.parts)} pozycji")
        print()
        print("=" * 42)

    def _choose_cabinet(self, title):
        """Wybór szafki z listy; None gdy brak szafek lub anulowano."""

        if not self.section.cabinets:
            print("\nSekcja nie zawiera jeszcze szafek.")
            return None

        return choose(
            self.section.cabinets,
            label=lambda c: (
                f"{c.cabinet_label}. {c.cabinet_type}   "
                f"{c.width}x{c.height}x{c.depth}"
            ),
            title=title,
            back="Anuluj"
        )

    def edit_cabinet(self):

        cabinet = self._choose_cabinet("Wybierz szafkę do edycji")

        if cabinet is None:
            return

        cabinet_type = choose(
            list(config.CABINET_TYPES),
            label=lambda name: name,
            title=f"Typ szafki (obecnie: {cabinet.cabinet_type})",
            back="Anuluj"
        )

        if cabinet_type is None:
            return

        print("\nENTER - zachowaj obecną wartość\n")

        dimensions = ask_cabinet_dimensions(
            cabinet.width, cabinet.height, cabinet.depth,
            cabinet.shelves, cabinet.fronts
        )

        try:
            CabinetService.update(
                project=self.project,
                cabinet=cabinet,
                cabinet_type=cabinet_type,
                **dimensions
            )

        except ValueError as error:
            print(f"\nNie można zaktualizować szafki: {error}")
            return

        self.project_manager.save_project(self.project)

        print(
            f"\nSzafka {cabinet.cabinet_label} zaktualizowana "
            f"({len(cabinet.parts)} formatek)."
        )

    def delete_cabinet(self):

        cabinet = self._choose_cabinet("Wybierz szafkę do usunięcia")

        if cabinet is None:
            return

        if not confirm(f"Usunąć szafkę {cabinet.cabinet_label}?"):
            print("Anulowano.")
            return

        CabinetService.delete(
            self.project,
            self.section,
            cabinet.cabinet_id
        )

        self.project_manager.save_project(self.project)

        print("\nSzafka została usunięta.")

    def show_parts(self):

        print("\n========================================")
        print("Lista formatek")
        print("========================================")

        if not self.section.cabinets:
            print("\nBrak szafek.")
            return

        for cabinet in self.section.cabinets:

            print(f"\nSzafka {cabinet.cabinet_label} - {cabinet.cabinet_type}\n")

            if not cabinet.parts:
                print("Brak formatek.")
                continue

            for part in cabinet.parts:
                print(
                    f"{part.part_label:<10}{part.part_name:<10}"
                    f"{part.length:>7} x{part.width:>7}"
                    f"{part.quantity:>4} szt.  {part.material}"
                )