"""Testy logiki biznesowej szafek."""

import pytest

from src.services.cabinet_service import CabinetService


def _create(project, section, **overrides):
    params = dict(
        cabinet_type="dolna",
        width=600, height=720, depth=560, shelves=1, fronts=2,
    )
    params.update(overrides)
    return CabinetService.create(project=project, section=section, **params)


def test_create_generates_parts(project, section):
    cabinet = _create(project, section)
    assert cabinet.cabinet_id == f"{project.project_id}-C001"
    assert cabinet.cabinet_label == "1.1"
    assert len(cabinet.parts) > 0


def test_create_rejects_unknown_type(project, section):
    with pytest.raises(ValueError):
        _create(project, section, cabinet_type="nieistniejąca")


def test_update_changes_dims_and_regenerates_parts(project, section):
    cabinet = _create(project, section, shelves=0)
    section.add_cabinet(cabinet)
    parts_before = list(cabinet.parts)

    CabinetService.update(
        project=project, cabinet=cabinet,
        cabinet_type="dolna",
        width=800, height=900, depth=560, shelves=3, fronts=2,
    )

    assert cabinet.width == 800
    assert cabinet.height == 900
    # inna liczba półek -> inny zestaw formatek
    assert cabinet.parts != parts_before


def test_find_missing_raises(section):
    with pytest.raises(LookupError):
        CabinetService.find(section, "P001-C999")


def test_delete_removes_and_relabels(project, section):
    first = _create(project, section)
    section.add_cabinet(first)
    second = _create(project, section)
    section.add_cabinet(second)

    CabinetService.delete(project, section, first.cabinet_id)

    assert len(section.cabinets) == 1
    assert section.cabinets[0].cabinet_id == second.cabinet_id
    assert section.cabinets[0].cabinet_label == "1.1"  # przenumerowana
