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
                print("\n=== Dodawanie sekcji ===\n")
                section_name = input("Podaj nazwę sekcji: ").strip()
                if not section_name:
                    print("Nazwa sekcji nie może być pusta.")
                else:
                    section = Section(name=section_name)
                    self.project.add_section(section)
                    self.project_manager.save_project(self.project)
                    print(f'Sekcja "{section_name}" została dodana.')
            elif choice == "2":
                print()
                if not self.project.sections:
                    print("Projekt nie zawiera jeszcze sekcji.")
                else:
                    print("Lista sekcji:\n")
                    for index, section in enumerate(
                            self.project.sections,
                            start=1):
                        print(f"{index}. {section.name}")
            elif choice == "3":
                print("Usuwanie sekcji - funkcja w przygotowaniu.")
            elif choice == "4":
                print("Zmiana nazwy sekcji - funkcja w przygotowaniu.")
            elif choice == "5":
                print("Otwarcie sekcji - funkcja w przygotowaniu.")
            elif choice == "0":
                break
            else:
                print("Nieprawidłowa opcja.")
            input("\nNaciśnij Enter, aby kontynuować...")

    def run(self):

       while True:

        choice = self.show()

        print()

        if choice == "1":
            print()
            print(f"ID projektu : {self.project.project_id}")
            print(f"Nazwa       : {self.project.project_name}")
            print(f"Sekcji      : {len(self.project.sections)}")
            print(f"Utworzono   : {self.project.created_at}")

        elif choice == "2":

            self.sections_menu()

        elif choice == "0":
            print("Zamykanie projektu...")
            break

        else:
            print("Nieprawidłowa opcja.")

        input("\nNaciśnij Enter, aby kontynuować...")