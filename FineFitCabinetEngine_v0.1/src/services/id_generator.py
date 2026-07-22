from src.models.section import Section


class IdGenerator:
    """
    Generator identyfikatorów systemowych.
    """

    @staticmethod
    def generate_section_id(project) -> str:
        highest = 0
        for section in project.sections:
            try:
                number = int(section.section_id.split("-S")[1])
                highest = max(highest, number)
            except (IndexError, ValueError):
                continue
        return f"{project.project_id}-S{highest + 1:03d}"

    @staticmethod
    def create_section(
            project,
            section_number,
            section_name):
        return Section(
            section_id=IdGenerator.generate_section_id(project),
            section_number=section_number,
            section_name=section_name
        )

    @staticmethod
    def generate_section_number(project) -> int:
        if not project.sections:
            return 1
        return max(
            section.section_number
            for section in project.sections
        ) + 1