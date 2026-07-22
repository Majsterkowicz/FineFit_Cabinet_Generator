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
        """Zwraca projekt jako słownik."""
        return asdict(self)