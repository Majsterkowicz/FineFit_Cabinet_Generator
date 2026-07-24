"""Testy parzystości CLI z API.

Sterujemy interaktywnymi przepływami przez podstawiony input() i sprawdzamy,
że operacje CLI zmieniają stan i utrwalają go tak samo jak API.
"""

import pytest

from src.core.project_workspace import ProjectWorkspace
from src.core.section_workspace import SectionWorkspace
from src.services.section_service import SectionService


@pytest.fixture
def feed_input(monkeypatch):
    """Podstawia kolejne odpowiedzi użytkownika w miejsce input()."""

    def _feed(*answers):
        answers_iter = iter(answers)
        monkeypatch.setattr("builtins.input", lambda *_: next(answers_iter))

    return _feed


# --- Sekcje: usuwanie i zmiana nazwy --------------------------------------


def test_cli_delete_section_persists(manager, project, feed_input):
    keep = SectionService.create(project, "Zostaje")
    project.add_section(keep)
    remove = SectionService.create(project, "Do usunięcia")
    project.add_section(remove)
    manager.save_project(project)

    workspace = ProjectWorkspace(project, manager)
    # choose -> "2" (druga sekcja), confirm -> "t"
    feed_input("2", "t")
    workspace.delete_section()

    reloaded = manager.load_project_by_id(project.project_id)
    names = [s.section_name for s in reloaded.sections]
    assert names == ["Zostaje"]


def test_cli_delete_section_cancelled(manager, project, feed_input):
    section = SectionService.create(project, "Sekcja")
    project.add_section(section)
    manager.save_project(project)

    workspace = ProjectWorkspace(project, manager)
    feed_input("1", "n")   # wybór sekcji, ale odmowa potwierdzenia
    workspace.delete_section()

    assert len(manager.load_project_by_id(project.project_id).sections) == 1


def test_cli_rename_section_persists(manager, project, feed_input):
    section = SectionService.create(project, "Stara nazwa")
    project.add_section(section)
    manager.save_project(project)

    workspace = ProjectWorkspace(project, manager)
    feed_input("1", "Nowa nazwa")
    workspace.rename_section()

    reloaded = manager.load_project_by_id(project.project_id)
    assert reloaded.sections[0].section_name == "Nowa nazwa"


# --- Projekt: usuwanie ----------------------------------------------------


def test_cli_delete_project(manager, project, feed_input):
    folder = manager.find_project_folder(project.project_id)

    workspace = ProjectWorkspace(project, manager)
    feed_input("t")
    result = workspace.delete_project()

    assert result is True
    assert not folder.exists()


def test_cli_delete_project_cancelled(manager, project, feed_input):
    workspace = ProjectWorkspace(project, manager)
    feed_input("n")
    assert workspace.delete_project() is False
    assert manager.find_project_folder(project.project_id).exists()


# --- Szafki: edycja i usuwanie --------------------------------------------


def test_cli_edit_cabinet_persists(manager, project, section, cabinet, feed_input):
    workspace = SectionWorkspace(project, section, manager)
    # wybór szafki -> "1", typ -> "1" (dolna), szerokość 800,
    # wysokość/głębokość/półki/fronty -> ENTER
    feed_input("1", "1", "800", "", "", "", "")
    workspace.edit_cabinet()

    reloaded = manager.load_project_by_id(project.project_id)
    assert reloaded.sections[0].cabinets[0].width == 800


def test_cli_delete_cabinet_persists(manager, project, section, cabinet, feed_input):
    workspace = SectionWorkspace(project, section, manager)
    feed_input("1", "t")   # wybór szafki, potwierdzenie
    workspace.delete_cabinet()

    reloaded = manager.load_project_by_id(project.project_id)
    assert reloaded.sections[0].cabinets == []


# --- Wycena ---------------------------------------------------------------


def test_cli_show_pricing(manager, project, section, cabinet, capsys):
    ProjectWorkspace(project, manager).show_pricing()

    output = capsys.readouterr().out
    assert "Wycena" in output
    assert "RAZEM" in output
    assert project.pricing["currency"] in output
