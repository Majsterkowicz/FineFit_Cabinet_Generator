from src.core.main_menu import MainMenu
from src.services.project_manager import ProjectManager
from src.core.project_workspace import ProjectWorkspace


class Application:

    def __init__(self):

        self.main_menu = MainMenu()

        self.project_manager = ProjectManager()

        self.current_project = None

    def create_project(self):

        print("=== Nowy projekt ===")
        print()

        project_name = input("Podaj nazwę projektu: ")

        self.current_project = self.project_manager.create_project(project_name)

        print()
        print("Projekt został utworzony.")
        print()
        print(f"ID projektu: {self.current_project.project_id}")
        print(f"Nazwa projektu: {self.current_project.project_name}")

        workspace = ProjectWorkspace(
        self.current_project,
        self.project_manager
        )       
        workspace.run()

    def run(self):

        while True:

            choice = self.main_menu.show()

            print()

            if choice == "1":
                self.create_project()

            elif choice == "2":
                print("Otwieranie projektu...")

            elif choice == "0":
                print("Do widzenia!")
                break

            else:
                print("Nieprawidłowa opcja.")

            input("\nNaciśnij Enter, aby kontynuować...")