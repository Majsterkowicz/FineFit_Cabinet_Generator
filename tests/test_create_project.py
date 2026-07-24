from src.services.project_manager import ProjectManager

manager = ProjectManager()

project = manager.create_project(
    "Karolina - Kuchnia"
)

print(project)