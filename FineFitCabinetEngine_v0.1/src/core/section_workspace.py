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
            print("3. Dodaj element")
            print("4. Usuń element")
            print("0. Powrót")

            choice = input("\nWybierz opcję: ")

            if choice == "1":
                self.show_section_info()
            elif choice == "2":
                self.show_cabinets()
            elif choice == "3":
                self.add_element()
            elif choice == "4":
                self.remove_element()
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

    def add_element(self):
        print("\nKreator elementów będzie dostępny w następnym etapie.")
        input("\nENTER - powrót")

    def remove_element(self):
        print("\nUsuwanie elementów będzie dostępne w następnym etapie.")
        input("\nENTER - powrót")