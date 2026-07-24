"""Testy generatora formatek korpusu."""

from src.models.cabinet import Cabinet
from src.models.project import Project
from src.models.section import Section
from src.generators.part_generator import PartGenerator


def _fixture_cabinet(shelves=1, fronts=2):
    project = Project(project_id="P999", project_name="Test")
    section = Section(section_id="P999-S001", section_number=1, section_name="S")
    cabinet = Cabinet(
        cabinet_id="P999-C001", cabinet_label="1.1", cabinet_type="dolna",
        width=600, height=720, depth=560, shelves=shelves, fronts=fronts,
    )
    section.add_cabinet(cabinet)
    project.add_section(section)
    return project, cabinet


def test_generate_body_shelf_back_front():
    project, cabinet = _fixture_cabinet(shelves=1, fronts=2)
    parts = PartGenerator.generate(project, cabinet)
    names = {part.part_name for part in parts}
    assert names == {"Bok", "Wieniec", "Półka", "Plecy", "Front"}


def test_no_shelves_omits_shelf_part():
    project, cabinet = _fixture_cabinet(shelves=0, fronts=2)
    names = {p.part_name for p in PartGenerator.generate(project, cabinet)}
    assert "Półka" not in names


def test_no_fronts_omits_front_part():
    project, cabinet = _fixture_cabinet(shelves=1, fronts=0)
    names = {p.part_name for p in PartGenerator.generate(project, cabinet)}
    assert "Front" not in names


def test_side_quantity_is_two():
    project, cabinet = _fixture_cabinet()
    sides = [p for p in PartGenerator.generate(project, cabinet)
             if p.part_name == "Bok"]
    assert sides[0].quantity == 2
