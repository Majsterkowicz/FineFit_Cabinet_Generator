from pathlib import Path


class ProjectManager:

    def __init__(self):
        self.projects_path = Path("projects")

    def get_projects_directory(self):
        return self.projects_path
