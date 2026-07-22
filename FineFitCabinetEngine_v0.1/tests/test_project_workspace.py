from src.core.project_workspace import ProjectWorkspace
from src.models.project import Project

project = Project(
    project_id="P999",
    project_name="Projekt testowy"
)

workspace = ProjectWorkspace(project)

choice = workspace.show()

print()
print(f"Wybrano: {choice}")