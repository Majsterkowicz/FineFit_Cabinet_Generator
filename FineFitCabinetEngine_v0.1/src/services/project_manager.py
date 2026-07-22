from pathlib import Path
import json

from src.models.project import Project


class ProjectManager:

    def __init__(self):
        self.projects_path = Path("projects")
        self.projects_path.mkdir(exist_ok=True)

    def get_projects_directory(self):
        return self.projects_path

    def get_next_project_id(self):

        projects = [
            folder
            for folder in self.projects_path.iterdir()
            if folder.is_dir() and folder.name.startswith("P")
        ]

        if not projects:
            return "P001"

        highest = max(
            int(folder.name.split("_")[0][1:])
            for folder in projects
        )

        return f"P{highest + 1:03d}"

    def create_project(self, project_name: str):

        project_id = self.get_next_project_id()

        folder_name = (
            f"{project_id}_"
            f"{project_name.replace(' ', '_').replace('-', '')}"
        )

        project_folder = self.projects_path / folder_name
        project_folder.mkdir()

        project = Project(
            project_id=project_id,
            project_name=project_name
        )

        json_path = project_folder / "project.json"

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(
                project.to_dict(),
                file,
                indent=4,
                ensure_ascii=False
            )

        return project

    def list_projects(self):

        projects = sorted(
            folder
            for folder in self.projects_path.iterdir()
            if folder.is_dir()
        )

        return projects

    def load_project(self, project_folder):

        json_path = project_folder / "project.json"

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return Project.from_dict(data)