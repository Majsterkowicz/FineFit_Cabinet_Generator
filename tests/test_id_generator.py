"""Testy generatora identyfikatorów i numeracji technologicznej."""

from src.models.cabinet import Cabinet
from src.models.project import Project
from src.models.section import Section
from src.services.id_generator import IdGenerator


def make_project(project_id="P001"):
    return Project(project_id=project_id, project_name="Projekt")


def make_section(project_id, number, section_id=None):
    if section_id is None:
        section_id = f"{project_id}-S{number:03d}"
    return Section(
        section_id=section_id,
        section_number=number,
        section_name=f"Sekcja {number}",
    )


# --- ID sekcji ------------------------------------------------------------


def test_first_section_id():
    project = make_project("P007")
    assert IdGenerator.generate_section_id(project) == "P007-S001"


def test_section_id_increments_past_highest():
    project = make_project("P007")
    project.add_section(make_section("P007", 1))
    project.add_section(make_section("P007", 2))
    assert IdGenerator.generate_section_id(project) == "P007-S003"


def test_section_id_ignores_malformed_ids():
    """Puste/uszkodzone ID nie mają wpływu na kolejny numer."""

    project = make_project("P007")
    project.add_section(make_section("P007", 5, section_id=""))
    project.add_section(make_section("P007", 1, section_id="P007-S001"))
    assert IdGenerator.generate_section_id(project) == "P007-S002"


# --- Backfill ID sekcji (regresja: puste section_id -> 405 przy usuwaniu) --


def test_backfill_fills_missing_section_id():
    project = make_project("P004")
    project.add_section(make_section("P004", 1, section_id=""))
    project.add_section(make_section("P004", 2, section_id="P004-S001"))
    project.add_section(make_section("P004", 3, section_id="P004-S002"))

    changed = IdGenerator.backfill_section_ids(project)

    assert changed is True
    assert project.sections[0].section_id == "P004-S003"
    ids = [s.section_id for s in project.sections]
    assert "" not in ids
    assert len(ids) == len(set(ids))  # brak duplikatów


def test_backfill_multiple_missing_ids_are_unique():
    project = make_project("P004")
    project.add_section(make_section("P004", 1, section_id=""))
    project.add_section(make_section("P004", 2, section_id=""))

    IdGenerator.backfill_section_ids(project)

    ids = [s.section_id for s in project.sections]
    assert "" not in ids
    assert len(ids) == len(set(ids))


def test_backfill_noop_returns_false():
    project = make_project("P004")
    project.add_section(make_section("P004", 1))
    assert IdGenerator.backfill_section_ids(project) is False


# --- ID szafek ------------------------------------------------------------


def test_cabinet_id_unique_across_sections():
    project = make_project("P002")
    section_a = make_section("P002", 1)
    section_b = make_section("P002", 2)
    section_a.add_cabinet(_cabinet("P002-C001"))
    project.add_section(section_a)
    project.add_section(section_b)
    assert IdGenerator.generate_cabinet_id(project) == "P002-C002"


# --- Przeliczanie numeracji -----------------------------------------------


def test_renumber_reorders_and_relabels():
    project = make_project("P003")
    second = make_section("P003", 2)
    first = make_section("P003", 1)
    first.add_cabinet(_cabinet("P003-C001"))
    first.add_cabinet(_cabinet("P003-C002"))
    project.add_section(second)   # celowo w złej kolejności
    project.add_section(first)

    IdGenerator.renumber_project(project)

    assert [s.section_number for s in project.sections] == [1, 2]
    labels = [c.cabinet_label for c in project.sections[0].cabinets]
    assert labels == ["1.1", "1.2"]


def _cabinet(cabinet_id):
    return Cabinet(
        cabinet_id=cabinet_id,
        cabinet_label="1.1",
        cabinet_type="dolna",
        width=600, height=720, depth=560, shelves=1, fronts=2,
    )
