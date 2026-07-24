from pathlib import Path
import json
import os
import shutil
import tempfile

from src import config
from src.models.project import Project


class ProjectManager:
    """Zapis i odczyt projektów. Jedno źródło prawdy dla CLI i API."""

    def __init__(self, projects_path=None):

        if projects_path is None:

            root = Path(__file__).resolve().parents[2]

            projects_path = root / config.PROJECTS_DIRECTORY

        self.projects_path = Path(projects_path)
        self.projects_path.mkdir(parents=True, exist_ok=True)

    def get_projects_directory(self):
        return self.projects_path

    def list_projects(self):
        """Foldery projektów posortowane po nazwie."""

        return sorted(
            folder
            for folder in self.projects_path.iterdir()
            if folder.is_dir() and (folder / "project.json").exists()
        )

    def get_next_project_id(self):

        highest = 0

        for folder in self.projects_path.iterdir():

            if not folder.is_dir():
                continue

            try:
                number = int(folder.name.split("_")[0][1:])

            except ValueError:
                continue

            highest = max(highest, number)

        digits = config.PROJECT_DIGITS

        return f"{config.PROJECT_PREFIX}{highest + 1:0{digits}d}"

    def create_project(self, project_name: str):

        name = (project_name or "").strip()

        if not name:
            raise ValueError("Nazwa projektu nie może być pusta.")

        project_id = self.get_next_project_id()

        folder_name = (
            f"{project_id}_"
            f"{name.replace(' ', '_').replace('-', '')}"
        )

        project_folder = self.projects_path / folder_name
        project_folder.mkdir()

        project = Project(
            project_id=project_id,
            project_name=name
        )

        self.save_project(project)

        return project

    def delete_project(self, project_id: str):
        """
        Usuwa folder projektu wraz z całą zawartością.

        find_project_folder zgłasza LookupError, gdy projekt nie istnieje -
        API tłumaczy to na kod 404.
        """

        project_folder = self.find_project_folder(project_id)

        shutil.rmtree(project_folder)

        return project_id

    def find_project_folder(self, project_id: str):
        """
        Zwraca folder projektu o podanym ID systemowym.

        Skanujemy katalogi bez wymogu istnienia project.json - metoda
        jest wołana także tuż po utworzeniu pustego folderu projektu.
        """

        for folder in self.projects_path.iterdir():

            if folder.is_dir() and folder.name.split("_")[0] == project_id:
                return folder

        raise LookupError(f"Nie znaleziono projektu {project_id}.")

    def load_project(self, project_folder):

        json_path = Path(project_folder) / "project.json"

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return Project.from_dict(data)

    def load_project_by_id(self, project_id: str):

        return self.load_project(self.find_project_folder(project_id))

    def save_project(self, project: Project):
        """
        Zapisuje projekt do pliku project.json.

        Zapis jest atomowy - plik docelowy nigdy nie pozostaje
        w stanie częściowo zapisanym.
        """

        project_folder = self.find_project_folder(project.project_id)

        json_path = project_folder / "project.json"

        descriptor, temporary_path = tempfile.mkstemp(
            dir=project_folder,
            suffix=".tmp"
        )

        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                json.dump(
                    project.to_dict(),
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(temporary_path, json_path)

        except BaseException:
            Path(temporary_path).unlink(missing_ok=True)
            raise

        return project
