class IdGenerator:
    """
    Generator identyfikatorów systemowych oraz numeracji technologicznej.

    Żaden inny moduł nie wyznacza własnych numerów.
    Generator nie tworzy modeli domenowych.
    """

    @staticmethod
    def _next_number(identifiers, separator: str) -> int:
        """Zwraca kolejny numer dla ID postaci PXXX-<separator>NNN."""

        highest = 0

        for identifier in identifiers:
            try:
                highest = max(highest, int(identifier.split(separator)[1]))
            except (IndexError, ValueError):
                continue

        return highest + 1

    @staticmethod
    def all_cabinets(project):
        for section in project.sections:
            yield from section.cabinets

    @staticmethod
    def all_parts(project):
        for cabinet in IdGenerator.all_cabinets(project):
            yield from cabinet.parts

    # --- Sekcje ---------------------------------------------------------

    @staticmethod
    def generate_section_id(project) -> str:

        number = IdGenerator._next_number(
            (section.section_id for section in project.sections),
            "-S"
        )

        return f"{project.project_id}-S{number:03d}"

    @staticmethod
    def generate_section_number(project) -> int:

        if not project.sections:
            return 1

        return max(
            section.section_number
            for section in project.sections
        ) + 1

    # --- Szafki ---------------------------------------------------------

    @staticmethod
    def generate_cabinet_id(project) -> str:

        number = IdGenerator._next_number(
            (
                cabinet.cabinet_id
                for cabinet in IdGenerator.all_cabinets(project)
            ),
            "-C"
        )

        return f"{project.project_id}-C{number:03d}"

    @staticmethod
    def format_cabinet_label(section_number: int, index: int) -> str:
        """Numeracja technologiczna szafki, np. 1.2"""

        return f"{section_number}.{index}"

    @staticmethod
    def generate_cabinet_label(section) -> str:

        highest = 0

        for cabinet in section.cabinets:
            try:
                highest = max(
                    highest,
                    int(cabinet.cabinet_label.split(".")[-1])
                )
            except (IndexError, ValueError):
                continue

        return IdGenerator.format_cabinet_label(
            section.section_number,
            highest + 1
        )

    # --- Elementy produkcyjne -------------------------------------------

    @staticmethod
    def next_part_number(project) -> int:
        """
        Pierwszy wolny numer elementu produkcyjnego.

        Numeracja całej serii wyznaczana jest jednym przebiegiem,
        bez ponownego przeszukiwania projektu dla każdej formatki.
        """

        return IdGenerator._next_number(
            (part.part_id for part in IdGenerator.all_parts(project)),
            "-P"
        )

    @staticmethod
    def format_part_id(project, number: int) -> str:

        return f"{project.project_id}-P{number:03d}"

    @staticmethod
    def generate_part_label(cabinet, index: int) -> str:
        """Numeracja technologiczna elementu, np. 1.2.3"""

        return f"{cabinet.cabinet_label}.{index}"

    # --- Przeliczanie numeracji -----------------------------------------

    @staticmethod
    def renumber_project(project):
        """
        Przelicza numerację technologiczną całego projektu.

        Numeracja technologiczna może ulegać zmianie,
        ID systemowe pozostają nietknięte.
        """

        project.sections.sort(key=lambda section: section.section_number)

        for section_number, section in enumerate(project.sections, start=1):

            section.section_number = section_number

            for cabinet_index, cabinet in enumerate(section.cabinets, start=1):

                cabinet.cabinet_label = IdGenerator.format_cabinet_label(
                    section_number,
                    cabinet_index
                )

                for part_index, part in enumerate(cabinet.parts, start=1):

                    part.part_label = IdGenerator.generate_part_label(
                        cabinet,
                        part_index
                    )

        return project
