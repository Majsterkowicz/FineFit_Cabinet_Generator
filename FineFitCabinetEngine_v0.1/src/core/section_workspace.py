from src.core.cabinet_wizard import CabinetWizard


class SectionWorkspace:

    def __init__(self, project, section, project_manager):

        self.project = project
        self.section = section
        self.project_manager = project_manager

    def run(self):

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
            print("4. Lista formatek")
            print("0. Powrót")

            choice = input("\nWybierz opcję: ")

            if choice == "1":
                self.show_section_info()
            elif choice == "2":
                self.show_cabinets()
            elif choice == "3":
                self.add_cabinet()
            elif choice == "4":
                self.show_parts()
            elif choice == "0":
                break
            else:
                print("\nNiepoprawny wybór.")

    def show_section_info(self):
        print("\n========================================")
        print("Informacje o sekcji")
        print("========================================")

        print(f"ID: {self.section.section_id}")
        print(f"Numer: {self.section.section_number}")
        print(f"Nazwa: {self.section.section_name}")
        print(f"Liczba szafek: {len(self.section.cabinets)}")

        input("\nENTER - powrót")

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
        input("\nENTER - powrót")

    def add_cabinet(self):

        wizard = CabinetWizard(self.project, self.section)

        cabinet = wizard.run()

        if cabinet is None:
            input("\nENTER - powrót")
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

        input("\nENTER - powrót")

    def show_parts(self):

        print("\n========================================")
        print("Lista formatek")
        print("========================================")

        if not self.section.cabinets:
            print("\nBrak szafek.")
            input("\nENTER - powrót")
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

        input("\nENTER - powrót")