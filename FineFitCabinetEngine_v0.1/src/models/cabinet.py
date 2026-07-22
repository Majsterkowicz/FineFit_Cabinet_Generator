from dataclasses import dataclass, field, asdict

from src.models.part import Part


@dataclass
class Cabinet:

    cabinet_id: str          # P015-E001

    cabinet_label: str       # 1.2

    cabinet_type: str

    width: int

    height: int

    depth: int

    shelves: int

    fronts: int

    parts: list[Part] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        return cls(
            cabinet_id=data["cabinet_id"],
            cabinet_label=data["cabinet_label"],
            cabinet_type=data["cabinet_type"],
            width=data["width"],
            height=data["height"],
            depth=data["depth"],
            shelves=data["shelves"],
            fronts=data["fronts"],
            parts=[
                Part.from_dict(part)
                for part in data.get("parts", [])
            ]
        )