from src.core.prompt import banner, confirm_save
from src.services.section_service import SectionService


class SectionWizard:

    def __init__(self, project):

        self.project = project

    def run(self):

        banner("Dodawanie sekcji")

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

        section_name = input("Podaj nazwę sekcji: ")

        # regułę pustej nazwy zna usługa - kreator tylko pokazuje komunikat
        try:
            section = SectionService.create(self.project, section_name)

        except ValueError as error:
            print(f"\n{error}")
            return None

        banner("Podsumowanie")

        print(f"Numer sekcji : {section.section_number}")
        print(f"Nazwa        : {section.section_name}")
        print()
        print("=" * 42)
        print()

        if not confirm_save():
            print("\nDodawanie sekcji anulowano.")
            return None

        return section
