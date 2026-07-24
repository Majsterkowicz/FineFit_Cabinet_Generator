"""Testy logiki biznesowej sekcji."""

import pytest

from src.services.section_service import SectionService


def test_create_assigns_id_and_number(project):
    section = SectionService.create(project, "Ściana lewa")
    assert section.section_id == f"{project.project_id}-S001"
    assert section.section_number == 1
    assert section.section_name == "Ściana lewa"


def test_create_rejects_empty_name(project):
    with pytest.raises(ValueError):
        SectionService.create(project, "   ")


def test_rename_keeps_id(project, section):
    original_id = section.section_id
    SectionService.rename(section, "Nowa nazwa")
    assert section.section_name == "Nowa nazwa"
    assert section.section_id == original_id


def test_rename_rejects_empty(section):
    with pytest.raises(ValueError):
        SectionService.rename(section, "")


def test_find_missing_raises(project):
    with pytest.raises(LookupError):
        SectionService.find(project, "P001-S999")


def test_delete_removes_and_renumbers(project):
    first = SectionService.create(project, "Pierwsza")
    project.add_section(first)
    second = SectionService.create(project, "Druga")
    project.add_section(second)

    SectionService.delete(project, first.section_id)

    assert len(project.sections) == 1
    assert project.sections[0].section_id == second.section_id
    assert project.sections[0].section_number == 1  # przenumerowana
