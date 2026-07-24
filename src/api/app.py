import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src import config
from src.api.schemas import CabinetInput, ProjectCreate, SectionName
from src.generators.bom_generator import BomGenerator
from src.generators.pricing_engine import PricingEngine
from src.services.cabinet_service import CabinetService
from src.services.project_manager import ProjectManager
from src.services.section_service import SectionService

ROOT = Path(__file__).resolve().parents[2]

WEB_DIRECTORY = ROOT / "web"

# Zasoby frontendu (JS/CSS) nie są wersjonowane w adresie, więc każą
# przeglądarce rewalidować je przy każdym wejściu (ETag -> 304, gdy bez
# zmian). Dzięki temu po zmianie kodu nie widać nieaktualnej wersji.
NO_CACHE = "no-cache"


class NoCacheStaticFiles(StaticFiles):

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = NO_CACHE
        return response

app = FastAPI(
    title="FineFit Cabinet Engine API",
    version="0.9.0"
)

project_manager = ProjectManager()


# --- Tłumaczenie wyjątków domenowych na kody HTTP -------------------------
#
# Usługi zgłaszają ValueError (dane niepoprawne) oraz LookupError
# (obiekt nie istnieje). Reguła jest jedna dla całego API, dzięki czemu
# nowy endpoint zachowuje się poprawnie bez dodatkowego kodu.


@app.exception_handler(ValueError)
def handle_value_error(request: Request, error: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(error)})


@app.exception_handler(LookupError)
def handle_lookup_error(request: Request, error: LookupError):
    return JSONResponse(status_code=404, content={"detail": str(error)})


# --- Konfiguracja ---------------------------------------------------------


@app.get("/api/config")
def get_config():
    """Typy szafek oraz stałe konstrukcyjne."""

    return {
        "cabinet_types": [
            {"name": name, **defaults}
            for name, defaults in config.CABINET_TYPES.items()
        ],
        **config.CONSTRUCTION
    }


# --- Projekty -------------------------------------------------------------


@app.get("/api/projects")
def list_projects():
    """
    Skrócona lista projektów.

    Czytamy surowy JSON i liczymy sekcje oraz szafki bez budowania
    modeli domenowych - lista nie potrzebuje formatek.
    """

    projects = []

    for folder in project_manager.list_projects():

        with open(folder / "project.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        sections = data.get("sections", [])

        projects.append({
            "project_id": data["project_id"],
            "project_name": data["project_name"],
            "created_at": data["created_at"],
            "sections": len(sections),
            "cabinets": sum(
                len(section.get("cabinets", []))
                for section in sections
            )
        })

    return projects


@app.post("/api/projects", status_code=201)
def create_project(payload: ProjectCreate):

    return project_manager.create_project(payload.project_name).to_dict()


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):

    return project_manager.load_project_by_id(project_id).to_dict()


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):

    project_manager.delete_project(project_id)

    return {"deleted": project_id}


# --- Sekcje ---------------------------------------------------------------


@app.post("/api/projects/{project_id}/sections", status_code=201)
def create_section(project_id: str, payload: SectionName):

    project = project_manager.load_project_by_id(project_id)

    section = SectionService.create(project, payload.section_name)

    project.add_section(section)
    project_manager.save_project(project)

    return section.to_dict()


@app.patch("/api/projects/{project_id}/sections/{section_id}")
def rename_section(project_id: str, section_id: str, payload: SectionName):

    project = project_manager.load_project_by_id(project_id)

    section = SectionService.rename(
        SectionService.find(project, section_id),
        payload.section_name
    )

    project_manager.save_project(project)

    return section.to_dict()


@app.delete("/api/projects/{project_id}/sections/{section_id}")
def delete_section(project_id: str, section_id: str):

    project = project_manager.load_project_by_id(project_id)

    SectionService.delete(project, section_id)
    project_manager.save_project(project)

    return {"deleted": section_id}


# --- Szafki ---------------------------------------------------------------


@app.post(
    "/api/projects/{project_id}/sections/{section_id}/cabinets",
    status_code=201
)
def create_cabinet(project_id: str, section_id: str, payload: CabinetInput):

    project = project_manager.load_project_by_id(project_id)
    section = SectionService.find(project, section_id)

    cabinet = CabinetService.create(
        project=project,
        section=section,
        **payload.model_dump()
    )

    section.add_cabinet(cabinet)
    project_manager.save_project(project)

    return cabinet.to_dict()


@app.put(
    "/api/projects/{project_id}/sections/{section_id}/cabinets/{cabinet_id}"
)
def update_cabinet(
        project_id: str,
        section_id: str,
        cabinet_id: str,
        payload: CabinetInput):

    project = project_manager.load_project_by_id(project_id)
    section = SectionService.find(project, section_id)

    cabinet = CabinetService.update(
        project=project,
        cabinet=CabinetService.find(section, cabinet_id),
        **payload.model_dump()
    )

    project_manager.save_project(project)

    return cabinet.to_dict()


@app.delete(
    "/api/projects/{project_id}/sections/{section_id}/cabinets/{cabinet_id}"
)
def delete_cabinet(project_id: str, section_id: str, cabinet_id: str):

    project = project_manager.load_project_by_id(project_id)
    section = SectionService.find(project, section_id)

    CabinetService.delete(project, section, cabinet_id)
    project_manager.save_project(project)

    return {"deleted": cabinet_id}


# --- Technologia ----------------------------------------------------------


@app.get("/api/projects/{project_id}/cutting-list")
def cutting_list(project_id: str, section_id: str = None):

    project = project_manager.load_project_by_id(project_id)

    parts = BomGenerator.collect_parts(project, section_id)

    return {
        "rows": BomGenerator.cutting_list(parts),
        "summary": BomGenerator.summary(parts)
    }


@app.get("/api/projects/{project_id}/pricing")
def pricing(project_id: str, section_id: str = None):

    project = project_manager.load_project_by_id(project_id)

    return PricingEngine.estimate(project, section_id)


@app.get("/api/projects/{project_id}/parts")
def list_parts(project_id: str, section_id: str = None):

    project = project_manager.load_project_by_id(project_id)

    return [
        part.to_dict()
        for part in BomGenerator.collect_parts(project, section_id)
    ]


# --- Frontend -------------------------------------------------------------


@app.get("/")
def index():

    return FileResponse(
        WEB_DIRECTORY / "index.html",
        headers={"Cache-Control": NO_CACHE}
    )


app.mount(
    "/static",
    NoCacheStaticFiles(directory=WEB_DIRECTORY),
    name="static"
)
