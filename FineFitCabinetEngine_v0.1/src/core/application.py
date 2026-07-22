from src.core.menu import Menu


class Application:

    def __init__(self):
        self.menu = Menu()

    def run(self):

        while True:

            choice = self.menu.show_main_menu()

            print()

            if choice == "1":
                print("Tworzenie nowego projektu...")

            elif choice == "2":
                print("Otwieranie projektu...")

            elif choice == "0":
                print("Do widzenia!")
                break

            else:
                print("Nieprawidłowa opcja.")

            input("\nNaciśnij Enter, aby kontynuować...")