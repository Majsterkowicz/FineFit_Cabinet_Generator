from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Project:
    project_id: str
    project_name: str
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    sections: list = field(default_factory=list)

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
            sections=data.get("sections", [])
        )