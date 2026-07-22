"""Wspólne elementy interfejsu tekstowego."""


def banner(title: str, width: int = 42):
    """Nagłówek ekranu."""

    print()
    print("=" * width)
    print(f" {title}")
    print("=" * width)
    print()


def confirm_save() -> bool:
    """
    Potwierdzenie zapisu zgodne ze standardem kreatorów.

    ENTER - zapisz, N - anuluj.
    """

    while True:

        choice = input("ENTER - zapisz | N - anuluj: ").strip().lower()

        if choice == "":
            return True

        if choice == "n":
            return False

        print("\nNieprawidłowy wybór. Naciśnij ENTER lub wpisz N.")


def choose(items, label, title="Wybierz", back="Powrót"):
    """
    Wyświetla ponumerowaną listę i zwraca wybrany element.

    Zwraca None, gdy użytkownik wybierze 0.
    """

    if not items:
        return None

    while True:

        print(f"\n{title}:\n")

        for index, item in enumerate(items, start=1):
            print(f"{index}. {label(item)}")

        print(f"\n0. {back}\n")

        choice = input("Twój wybór: ").strip()

        if choice == "0":
            return None

        try:
            index = int(choice) - 1

            if index < 0 or index >= len(items):
                raise IndexError

        except (ValueError, IndexError):
            print("\nNieprawidłowy wybór.")
            continue

        return items[index]


def ask_number(prompt: str, default, minimum: int = 1) -> int:
    """Liczba całkowita; ENTER przyjmuje wartość domyślną."""

    while True:

        value = input(f"{prompt} [{default}]: ").strip()

        if value == "":
            return default

        try:
            number = int(value)

        except ValueError:
            print("Podaj liczbę całkowitą.")
            continue

        if number < minimum:
            print(f"Wartość nie może być mniejsza niż {minimum}.")
            continue

        return number
