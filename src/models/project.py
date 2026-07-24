from dataclasses import dataclass, field, asdict
from datetime import datetime

from src.models.section import Section


@dataclass
class Project:
    project_id: str
    project_name: str
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    sections: list[Section] = field(default_factory=list)

    # Migawka cennika z chwili utworzenia projektu (patrz PricingEngine.snapshot).
    # Pusty słownik oznacza projekt sprzed wprowadzenia wyceny - uzupełniany
    # przy wczytaniu (ProjectManager.load_project).
    pricing: dict = field(default_factory=dict)

    def to_dict(self):
        """Konwersja obiektu Project do słownika."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Tworzy obiekt Project ze słownika."""
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            created_at=data["created_at"],
            sections=[
                Section.from_dict(section)
                for section in data.get("sections", [])
            ],
            pricing=data.get("pricing", {})
        )
    def add_section(self, section):
        """Dodaje sekcję do projektu."""
        self.sections.append(section)