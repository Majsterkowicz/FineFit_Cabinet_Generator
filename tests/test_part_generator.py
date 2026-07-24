from src.generators.part_generator import PartGenerator
from src.models.cabinet import Cabinet
from src.models.project import Project
from src.models.section import Section

project = Project(
    project_id="P999",
    project_name="Projekt testowy"
)

section = Section(
    section_id="P999-S001",
    section_number=1,
    section_name="Sciana"
)

cabinet = Cabinet(
    cabinet_id="P999-C001",
    cabinet_label="1.1",
    cabinet_type="dolna",
    width=600,
    height=720,
    depth=560,
    shelves=1,
    fronts=2
)

section.add_cabinet(cabinet)
project.add_section(section)

parts = PartGenerator.generate(project, cabinet)
cabinet.parts = parts

print()
print("=" * 78)
print(f" Lista formatek - szafka {cabinet.cabinet_label} ({cabinet.cabinet_id})")
print("=" * 78)
print()

print(
    f"{'ID':<12}{'Nr':<8}{'Nazwa':<10}"
    f"{'Dlugosc':>9}{'Szer.':>8}{'Gr.':>6}{'Szt.':>6}  Material"
)
print("-" * 78)

for part in parts:
    print(
        f"{part.part_id:<12}{part.part_label:<8}{part.part_name:<10}"
        f"{part.length:>9}{part.width:>8}{part.thickness:>6}"
        f"{part.quantity:>6}  {part.material}"
    )

print("-" * 78)
print(f"Pozycji: {len(parts)}   Sztuk: {sum(p.quantity for p in parts)}")
print()
