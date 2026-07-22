from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Project:
    project_id: str
    project_name: str
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    sections: list = field(default_factory=list)