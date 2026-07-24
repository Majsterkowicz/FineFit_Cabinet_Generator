"""Testy wyceny projektu (PricingEngine)."""

from src.generators.pricing_engine import PricingEngine
from src.services.cabinet_service import CabinetService


def _add_cabinet(project, section, **overrides):
    params = dict(
        cabinet_type="dolna",
        width=600, height=720, depth=560, shelves=1, fronts=2,
    )
    params.update(overrides)
    cabinet = CabinetService.create(project=project, section=section, **params)
    section.add_cabinet(cabinet)
    return cabinet


def test_empty_project_costs_zero(project):
    estimate = PricingEngine.estimate(project)
    assert estimate["total"] == 0
    assert estimate["currency"] == project.pricing["currency"]


def test_estimate_has_all_sections(project, cabinet):
    estimate = PricingEngine.estimate(project)
    assert {"currency", "materials", "edging", "hardware", "total"} <= set(estimate)
    assert estimate["total"] > 0


def test_material_cost_is_area_times_price(project, cabinet):
    estimate = PricingEngine.estimate(project)
    prices = project.pricing["material_prices"]

    for line in estimate["materials"]:
        assert line["unit_price"] == prices[line["material"]]
        assert line["cost"] == round(line["area"] * prices[line["material"]], 2)


def test_hardware_derived_from_fronts(project, section):
    _add_cabinet(project, section, fronts=2)
    estimate = PricingEngine.estimate(project)

    hardware = {line["name"]: line for line in estimate["hardware"]}
    # 2 fronty -> 2 uchwyty, 2 * hinges_per_front zawiasów
    assert hardware["Uchwyty"]["quantity"] == 2
    assert hardware["Zawiasy"]["quantity"] == 2 * project.pricing["hinges_per_front"]


def test_total_is_sum_of_lines(project, section):
    _add_cabinet(project, section)
    _add_cabinet(project, section)
    estimate = PricingEngine.estimate(project)

    parts_total = (
        sum(line["cost"] for line in estimate["materials"])
        + estimate["edging"]["cost"]
        + sum(line["cost"] for line in estimate["hardware"])
    )
    assert estimate["total"] == round(parts_total, 2)


def test_section_filter_scopes_estimate(project):
    from src.services.section_service import SectionService

    first = SectionService.create(project, "Pierwsza")
    project.add_section(first)
    _add_cabinet(project, first)

    second = SectionService.create(project, "Druga")
    project.add_section(second)

    # Wycena tylko pustej sekcji = 0, mimo że projekt zawiera szafkę.
    scoped = PricingEngine.estimate(project, second.section_id)
    assert scoped["total"] == 0

    full = PricingEngine.estimate(project)
    assert full["total"] > 0
