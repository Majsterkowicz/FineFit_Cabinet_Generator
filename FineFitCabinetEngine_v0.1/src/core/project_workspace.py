class ProjectWorkspace:

    def __init__(self, project):
        self.project = project

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