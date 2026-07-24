"""Testy zapisu, odczytu i usuwania projektów."""

import json

import pytest

from src.services.section_service import SectionService


def test_create_project_persists_json(manager):
    project = manager.create_project("Karolina - Kuchnia")

    folder = manager.find_project_folder(project.project_id)
    assert (folder / "project.json").exists()
    assert project.project_id == "P001"


def test_create_project_increments_id(manager):
    first = manager.create_project("Pierwszy")
    second = manager.create_project("Drugi")
    assert (first.project_id, second.project_id) == ("P001", "P002")


def test_create_project_rejects_empty_name(manager):
    with pytest.raises(ValueError):
        manager.create_project("   ")


def test_load_round_trip(manager):
    project = manager.create_project("Projekt")
    project.add_section(SectionService.create(project, "Ściana"))
    manager.save_project(project)

    reloaded = manager.load_project_by_id(project.project_id)
    assert reloaded.project_name == "Projekt"
    assert len(reloaded.sections) == 1
    assert reloaded.sections[0].section_name == "Ściana"


def test_delete_project_removes_folder(manager):
    project = manager.create_project("Do usunięcia")
    folder = manager.find_project_folder(project.project_id)

    manager.delete_project(project.project_id)

    assert not folder.exists()
    with pytest.raises(LookupError):
        manager.find_project_folder(project.project_id)


def test_delete_missing_project_raises(manager):
    with pytest.raises(LookupError):
        manager.delete_project("P999")


def test_list_projects_sorted(manager):
    manager.create_project("A")
    manager.create_project("B")
    folders = manager.list_projects()
    assert folders == sorted(folders)
    assert len(folders) == 2


# --- Migracja legacy: puste section_id uzupełniane przy wczytaniu ---------


def test_load_backfills_and_persists_missing_section_id(manager):
    """Projekt zapisany bez section_id (starsza wersja) leczy się na wczytaniu."""

    project = manager.create_project("Legacy")
    folder = manager.find_project_folder(project.project_id)
    json_path = folder / "project.json"

    # Ręcznie psujemy dane: sekcja bez section_id, jak w starych projektach.
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["sections"] = [{
        "section_id": "",
        "section_number": 1,
        "section_name": "Stara sekcja",
        "cabinets": [],
    }]
    json_path.write_text(json.dumps(data), encoding="utf-8")

    loaded = manager.load_project_by_id(project.project_id)

    # ID uzupełnione w pamięci...
    assert loaded.sections[0].section_id != ""
    # ...oraz utrwalone na dysku.
    on_disk = json.loads(json_path.read_text(encoding="utf-8"))
    assert on_disk["sections"][0]["section_id"] != ""
