from dataclasses import dataclass, asdict


@dataclass
class Cabinet:

    cabinet_name: str

    width: int

    height: int

    depth: int

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        return cls(
            cabinet_name=data["cabinet_name"],
            width=data["width"],
            height=data["height"],
            depth=data["depth"]
        )