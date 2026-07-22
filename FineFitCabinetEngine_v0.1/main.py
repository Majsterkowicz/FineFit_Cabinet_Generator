from src.core.menu import Menu


def main():

    menu = Menu()

    choice = menu.show_main_menu()

    print()
    print(f"Wybrano opcję: {choice}")


if __name__ == "__main__":
    main()