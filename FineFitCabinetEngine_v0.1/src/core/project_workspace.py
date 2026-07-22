from src.models.section import Section

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
        print("2. Dodaj sekcję")
        print("0. Zamknij projekt")

        print()
        print("=" * 42)

        return input("Twój wybór: ")

    def run(self):

       while True:

        choice = self.show()

        print()

        if choice == "1":
            print("Informacje o projekcie - funkcja w przygotowaniu.")

        elif choice == "2":

            print("\n=== Dodawanie sekcji ===\n")

            section_name = input("Podaj nazwę sekcji: ").strip()

            if not section_name:
                print("Nazwa sekcji nie może być pusta.")

            else:
                section = Section(name=section_name)
                self.project.add_section(section)
                self.project_manager.save_project(self.project)
                print(f'Sekcja "{section_name}" została dodana i zapisana.')

        elif choice == "0":
            print("Zamykanie projektu...")
            break

        else:
            print("Nieprawidłowa opcja.")

        input("\nNaciśnij Enter, aby kontynuować...")