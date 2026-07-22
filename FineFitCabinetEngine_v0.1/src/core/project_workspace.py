from src.core.section_wizard import SectionWizard

class ProjectWorkspace:

    def __init__(self, project, project_manager):
        self.project = project
        self.project_manager = project_manager

    def show(self):

        print()
        print("=" * 42)
        print(" FineFit Cabinet Engine")
        print("=" * 42)
        print()

        print(f"Projekt: {self.project.project_id}")
        print(self.project.project_name)

        print()
        print("=" * 42)
        print()

        print("1. Informacje o projekcie")
        print("2. Zarządzaj sekcjami")
        print("0. Zamknij projekt")

        print()
        print("=" * 42)

        return input("Twój wybór: ")

    def sections_menu(self):
        while True:
            print()
            print("=" * 42)
            print(" Zarządzanie sekcjami")
            print("=" * 42)
            print()

            print("1. Dodaj sekcję")
            print("2. Lista sekcji")
            print("3. Usuń sekcję")
            print("4. Zmień nazwę sekcji")
            print("5. Otwórz sekcję")
            print("0. Powrót")

            print()
            print("=" * 42)

            choice = input("Twój wybór: ")

            if choice == "1":
                self.add_section()
            elif choice == "2":
                self.list_sections()
            elif choice == "3":
                self.delete_section()
            elif choice == "4":
                self.rename_section()
            elif choice == "5":
                self.open_section()
            elif choice == "0":
                break
            else:
                print("Nieprawidłowa opcja.")
            input("\nNaciśnij Enter, aby kontynuować...")

    def add_section(self):
        wizard = SectionWizard(self.project)
        section = wizard.run()
        if section is None:
            return
        self.project.add_section(section)
        self.project_manager.save_project(
            self.project
        )
        print()
        print("=" * 42)
        print(" Sekcja została dodana")
        print("=" * 42)
        print()
        print(f"ID systemowe : {section.section_id}")
        print(f"Numer sekcji : {section.section_number}")
        print(f"Nazwa        : {section.section_name}")
        print()
        print("=" * 42)

    def list_sections(self):
        print()
        if not self.project.sections:
            print("Projekt nie zawiera jeszcze sekcji.")
            return
        print("Lista sekcji:\n")
        for section in self.project.sections:
            print(
                f"{section.section_number}. "
                f"{section.section_name}"
            )

    def delete_section(self):
        print("Usuwanie sekcji - funkcja w przygotowaniu.")

    def rename_section(self):
        print("Zmiana nazwy sekcji - funkcja w przygotowaniu.")

    def open_section(self):
        print("Otwieranie sekcji - funkcja w przygotowaniu.")

    def show_project_info(self):
        print()

        print(f"ID projektu : {self.project.project_id}")
        print(f"Nazwa       : {self.project.project_name}")
        print(f"Sekcji      : {len(self.project.sections)}")
        print(f"Utworzono   : {self.project.created_at}")
        
    def run(self):

        while True:
            choice = self.show()
            print()
            if choice == "1":
                self.show_project_info()
            elif choice == "2":
                self.sections_menu()
            elif choice == "0":
                print("Zamykanie projektu...")
                break
            else:
                print("Nieprawidłowa opcja.")
            input("\nNaciśnij Enter, aby kontynuować...")