from src.core.project_workspace import ProjectWorkspace
from src.models.project import Project
from src.services.project_manager import ProjectManager

project = Project(
    project_id="P999",
    project_name="Projekt testowy"
)

project_manager = ProjectManager()

workspace = ProjectWorkspace(
    project,
    project_manager
    )

choice = workspace.show()

print()
print(f"Wybrano: {choice}")