from dataclasses import dataclass, field, asdict

from src.models.cabinet import Cabinet


@dataclass
class Section:

    section_name: str

    cabinets: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        section_name = data.get("section_name", data.get("name"))

        return cls(
            section_name=section_name,
            cabinets=[
                Cabinet.from_dict(cabinet)
                for cabinet in data.get("cabinets", [])
            ]
        )

    def add_cabinet(self, cabinet):

        self.cabinets.append(cabinet)