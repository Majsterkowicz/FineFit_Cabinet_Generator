"""Testy ustawień globalnych oraz migawki cennika projektu."""

import json

from src import config
from src.services.settings_manager import SettingsManager, settings_manager


# --- SettingsManager ------------------------------------------------------


def test_load_returns_defaults_when_missing(tmp_path):
    manager = SettingsManager(settings_path=tmp_path / "settings.json")
    settings = manager.load()
    assert settings["currency"] == config.DEFAULT_SETTINGS["currency"]
    assert "dolna" in settings["cabinet_types"]


def test_save_then_load_roundtrip(tmp_path):
    manager = SettingsManager(settings_path=tmp_path / "settings.json")
    settings = manager.load()
    settings["currency"] = "EUR"
    manager.save(settings)
    assert manager.load()["currency"] == "EUR"


def test_save_merges_missing_sections(tmp_path):
    """Zapis częściowych ustawień uzupełnia brakujące sekcje z domyślnych."""

    manager = SettingsManager(settings_path=tmp_path / "settings.json")
    saved = manager.save({"currency": "USD"})
    assert saved["currency"] == "USD"
    assert "construction" in saved and "cabinet_types" in saved


# --- Migawka cennika projektu --------------------------------------------


def test_new_project_snapshots_pricing(manager):
    project = manager.create_project("Projekt")
    assert project.pricing["currency"] == config.DEFAULT_SETTINGS["currency"]
    assert "material_prices" in project.pricing


def test_pricing_snapshot_is_independent_of_later_settings(manager):
    """Zmiana ustawień globalnych nie zmienia istniejących wycen."""

    before = manager.create_project("Przed")

    settings = settings_manager.load()
    settings["currency"] = "EUR"
    settings_manager.save(settings)

    after = manager.create_project("Po")

    assert before.pricing["currency"] == "PLN"
    assert after.pricing["currency"] == "EUR"

    # Ponowne wczytanie starego projektu zachowuje jego migawkę.
    reloaded = manager.load_project_by_id(before.project_id)
    assert reloaded.pricing["currency"] == "PLN"


def test_legacy_project_backfills_pricing(manager):
    """Projekt sprzed wprowadzenia wyceny dostaje migawkę przy wczytaniu."""

    project = manager.create_project("Legacy")
    json_path = manager.find_project_folder(project.project_id) / "project.json"

    data = json.loads(json_path.read_text(encoding="utf-8"))
    del data["pricing"]
    json_path.write_text(json.dumps(data), encoding="utf-8")

    loaded = manager.load_project_by_id(project.project_id)
    assert loaded.pricing  # uzupełnione w pamięci

    on_disk = json.loads(json_path.read_text(encoding="utf-8"))
    assert on_disk.get("pricing")  # oraz utrwalone


def test_new_cabinet_type_from_settings_is_usable(manager, client):
    """Typ szafki dodany w ustawieniach jest akceptowany przy tworzeniu szafki."""

    settings = settings_manager.load()
    settings["cabinet_types"]["nietypowa"] = {
        "width": 400, "height": 400, "depth": 400, "shelves": 0, "fronts": 1
    }
    settings_manager.save(settings)

    project_id = client.post(
        "/api/projects", json={"project_name": "T"}).json()["project_id"]
    section_id = client.post(
        f"/api/projects/{project_id}/sections",
        json={"section_name": "S"}).json()["section_id"]

    response = client.post(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets",
        json=dict(cabinet_type="nietypowa", width=400, height=400,
                  depth=400, shelves=0, fronts=1),
    )
    assert response.status_code == 201
