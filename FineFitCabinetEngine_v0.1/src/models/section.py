from dataclasses import dataclass, field, asdict

from src.models.cabinet import Cabinet


@dataclass
class Section:

    section_id: str
    section_number: int
    section_name: str

    cabinets: list[Cabinet] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        section_name = data.get("section_name", data.get("name"))
        section_id = data.get("section_id", "")
        section_number = int(data.get("section_number") or 0)

        return cls(
            section_id=section_id,
            section_number=section_number,
            section_name=section_name,
            cabinets=[
                Cabinet.from_dict(cabinet)
                for cabinet in data.get("cabinets", [])
            ]
        )

    def add_cabinet(self, cabinet):

        self.cabinets.append(cabinet)