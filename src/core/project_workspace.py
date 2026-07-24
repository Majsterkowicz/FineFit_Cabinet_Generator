from src.core.prompt import choose, confirm
from src.core.section_wizard import SectionWizard
from src.core.section_workspace import SectionWorkspace
from src.services.section_service import SectionService

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
        print("3. Usuń projekt")
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

    def _choose_section(self, title):
        """Wybór sekcji z listy; None gdy brak sekcji lub anulowano."""

        if not self.project.sections:
            print("\nProjekt nie zawiera jeszcze sekcji.")
            return None

        return choose(
            sorted(self.project.sections, key=lambda s: s.section_number),
            label=lambda s: f"{s.section_number}. {s.section_name}",
            title=title,
            back="Anuluj"
        )

    def delete_section(self):

        section = self._choose_section("Wybierz sekcję do usunięcia")

        if section is None:
            return

        if not confirm(
                f"Usunąć sekcję „{section.section_name}” wraz z szafkami?"):
            print("Anulowano.")
            return

        SectionService.delete(self.project, section.section_id)
        self.project_manager.save_project(self.project)

        print("\nSekcja została usunięta.")

    def rename_section(self):

        section = self._choose_section("Wybierz sekcję do zmiany nazwy")

        if section is None:
            return

        new_name = input(f"Nowa nazwa [{section.section_name}]: ").strip()

        if new_name == "":
            print("Nazwa nie może być pusta. Anulowano.")
            return

        SectionService.rename(section, new_name)
        self.project_manager.save_project(self.project)

        print("\nNazwa sekcji została zmieniona.")

    def open_section(self):

        section = self._choose_section("Wybierz sekcję")

        if section is None:
            return

        SectionWorkspace(
            self.project,
            section,
            self.project_manager
        ).run()

    def show_project_info(self):
        print()

        print(f"ID projektu : {self.project.project_id}")
        print(f"Nazwa       : {self.project.project_name}")
        print(f"Sekcji      : {len(self.project.sections)}")
        print(f"Utworzono   : {self.project.created_at}")
        
    def delete_project(self):
        """Usuwa cały projekt. Zwraca True, gdy projekt został usunięty."""

        if not confirm(
                f"Usunąć projekt „{self.project.project_name}” wraz z całą "
                f"zawartością?"):
            print("Anulowano.")
            return False

        self.project_manager.delete_project(self.project.project_id)
        print("\nProjekt został usunięty.")
        return True

    def run(self):

        while True:
            choice = self.show()
            print()
            if choice == "1":
                self.show_project_info()
            elif choice == "2":
                self.sections_menu()
            elif choice == "3":
                if self.delete_project():
                    break
            elif choice == "0":
                print("Zamykanie projektu...")
                break
            else:
                print("Nieprawidłowa opcja.")
            input("\nNaciśnij Enter, aby kontynuować...")