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

        section_number = input(
            "Podaj numer sekcji: "
        ).strip()

        if not section_number:

            print("\nNumer sekcji nie może być pusty.")
            return None

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

        print(f"Numer : {section_number}")
        print(f"Nazwa : {section_name}")

        print()

        confirm = input(
            "Zapisać sekcję? (t/n): "
        ).lower()

        if confirm != "t":

            print("\nAnulowano.")
            return None

        return IdGenerator.create_section(
            project=self.project,
            section_number=section_number,
            section_name=section_name
        )