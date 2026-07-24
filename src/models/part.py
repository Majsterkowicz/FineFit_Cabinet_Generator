from dataclasses import dataclass, asdict


@dataclass
class Part:
    """Element produkcyjny (formatka) należący do szafki."""

    part_id: str             # P020-P001

    part_label: str          # 1.2.1

    part_name: str           # Bok

    part_type: str           # bok | wieniec | polka | plecy | front

    length: float

    width: float

    thickness: float

    quantity: int

    material: str

    # Oklejanie krawędzi (0 = brak okleiny)

    edge_length_1: float = 0.0

    edge_length_2: float = 0.0

    edge_width_1: float = 0.0

    edge_width_2: float = 0.0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        return cls(
            part_id=data["part_id"],
            part_label=data["part_label"],
            part_name=data["part_name"],
            part_type=data["part_type"],
            length=data["length"],
            width=data["width"],
            thickness=data["thickness"],
            quantity=data["quantity"],
            material=data["material"],
            edge_length_1=data.get("edge_length_1", 0.0),
            edge_length_2=data.get("edge_length_2", 0.0),
            edge_width_1=data.get("edge_width_1", 0.0),
            edge_width_2=data.get("edge_width_2", 0.0)
        )
