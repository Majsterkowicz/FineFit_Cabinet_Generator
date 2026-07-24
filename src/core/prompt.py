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


def confirm(question: str, default: bool = False) -> bool:
    """
    Pytanie tak/nie. ENTER przyjmuje wartość domyślną.

    Dla operacji nieodwracalnych (usuwanie) domyślną wartością jest False,
    aby przypadkowy ENTER niczego nie skasował.
    """

    hint = "T/n" if default else "t/N"

    while True:

        choice = input(f"{question} [{hint}]: ").strip().lower()

        if choice == "":
            return default

        if choice in ("t", "tak"):
            return True

        if choice in ("n", "nie"):
            return False

        print("Wpisz T (tak) lub N (nie).")


def ask_cabinet_dimensions(width, height, depth, shelves, fronts) -> dict:
    """
    Pyta o wymiary szafki, przyjmując podane wartości jako domyślne.

    Jedno źródło etykiet i ograniczeń dla tworzenia (wartości domyślne typu)
    oraz edycji (obecne wartości szafki).
    """

    return {
        "width": ask_number("Szerokość [mm]", width),
        "height": ask_number("Wysokość  [mm]", height),
        "depth": ask_number("Głębokość [mm]", depth),
        "shelves": ask_number("Liczba półek ", shelves, minimum=0),
        "fronts": ask_number("Liczba frontów", fronts, minimum=0),
    }


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
