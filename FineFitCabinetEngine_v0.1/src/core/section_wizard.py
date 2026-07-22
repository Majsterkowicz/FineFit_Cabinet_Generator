from src.services.id_generator import IdGenerator


class SectionWizard:

    def __init__(self, project):

        self.project = project

    def run(self):

        print()
        print("=" * 42)
        print(" Dodawanie sekcji")
        print("=" * 42)

        print()

        if self.project.sections:
            print("Istniejące sekcje:\n")
            for section in sorted(
                self.project.sections,
                key=lambda s: s.section_number
            ):
                print(
                    f"{section.section_number}. "
                    f"{section.section_name}"
                )
        else:
            print("Projekt nie zawiera jeszcze sekcji.")
        print()
        print("-" * 42)
        print()
        section_number = IdGenerator.generate_section_number(
            self.project
        )
        print(f"Tworzona sekcja nr: {section_number}")
        print()

        section_name = input(
            "Podaj nazwę sekcji: "
        ).strip()

        if not section_name:

            print("\nNazwa sekcji nie może być pusta.")
            return None

        print()
        print("=" * 42)
        print(" Podsumowanie")
        print("=" * 42)
        print()
        print(f"Numer sekcji : {section_number}")
        print(f"Nazwa         : {section_name}")
        print()
        print("=" * 42)
        print()

        while True:
            confirm = input(
                "ENTER - zapisz | N - anuluj: "
            ).lower()

            if confirm == "":
                break

            if confirm == "n":
                print("\nDodawanie sekcji anulowano.")
                return None

            print("\nNieprawidłowy wybór. Naciśnij ENTER lub wpisz N.")

        return IdGenerator.create_section(
            project=self.project,
            section_number=section_number,
            section_name=section_name
        )
