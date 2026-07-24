from src.models.section import Section
from src.services.id_generator import IdGenerator


class SectionService:
    """
    Logika biznesowa sekcji.

    Usługa nie komunikuje się z użytkownikiem i nie zapisuje
    projektu. Korzysta z niej zarówno interfejs tekstowy (CLI),
    jak i API.
    """

    @staticmethod
    def create(project, section_name: str):
        """Tworzy nową sekcję i nadaje jej numerację."""

        name = (section_name or "").strip()

        if not name:
            raise ValueError("Nazwa sekcji nie może być pusta.")

        return Section(
            section_id=IdGenerator.generate_section_id(project),
            section_number=IdGenerator.generate_section_number(project),
            section_name=name
        )

    @staticmethod
    def find(project, section_id: str):
        """Zwraca sekcję o podanym ID systemowym."""

        for section in project.sections:
            if section.section_id == section_id:
                return section

        raise LookupError(f"Nie znaleziono sekcji {section_id}.")

    @staticmethod
    def rename(section, section_name: str):
        """Zmienia nazwę sekcji. ID systemowe pozostaje bez zmian."""

        name = (section_name or "").strip()

        if not name:
            raise ValueError("Nazwa sekcji nie może być pusta.")

        section.section_name = name

        return section

    @staticmethod
    def delete(project, section_id: str):
        """
        Usuwa sekcję i przelicza numerację technologiczną.

        ID systemowe usuniętej sekcji nie jest ponownie
        wykorzystywane.
        """

        section = SectionService.find(project, section_id)

        project.sections.remove(section)

        IdGenerator.renumber_project(project)

        return section
