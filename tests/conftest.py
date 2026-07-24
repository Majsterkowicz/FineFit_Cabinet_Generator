"""Wspólne fixtury testowe.

Każdy test dostaje odizolowany katalog projektów (tmp_path), więc testy
nigdy nie dotykają prawdziwych danych w projects/.
"""

import pytest
from fastapi.testclient import TestClient

from src.services.cabinet_service import CabinetService
from src.services.project_manager import ProjectManager
from src.services.section_service import SectionService


@pytest.fixture
def manager(tmp_path):
    """ProjectManager działający na tymczasowym katalogu projektów."""

    return ProjectManager(projects_path=tmp_path / "projects")


@pytest.fixture
def project(manager):
    """Świeży, zapisany projekt gotowy do dalszych operacji."""

    return manager.create_project("Kuchnia testowa")


@pytest.fixture
def section(manager, project):
    """Projekt z jedną zapisaną sekcją; zwraca tę sekcję."""

    created = SectionService.create(project, "Ściana lewa")
    project.add_section(created)
    manager.save_project(project)
    return created


@pytest.fixture
def cabinet(manager, project, section):
    """Sekcja z jedną szafką (wraz z formatkami); zwraca tę szafkę."""

    created = CabinetService.create(
        project=project,
        section=section,
        cabinet_type="dolna",
        width=600, height=720, depth=560, shelves=1, fronts=2,
    )
    section.add_cabinet(created)
    manager.save_project(project)
    return created


@pytest.fixture
def client(tmp_path, monkeypatch):
    """TestClient API z magazynem projektów odizolowanym do tmp_path.

    Endpointy sięgają po globalny `project_manager` z modułu app przy każdym
    wywołaniu, więc podmiana atrybutu modułu wystarcza do izolacji.
    """

    from src.api import app as app_module

    monkeypatch.setattr(
        app_module,
        "project_manager",
        ProjectManager(projects_path=tmp_path / "projects"),
    )

    return TestClient(app_module.app)
