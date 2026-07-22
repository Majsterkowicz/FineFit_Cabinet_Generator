from src.services.project_manager import ProjectManager

manager = ProjectManager()

projects = manager.list_projects()

print("Lista projektów:")

for index, project in enumerate(projects, start=1):
    print(f"{index}. {project.name}")

print()

loaded = manager.load_project(projects[0])

print("Załadowany projekt:")

print(loaded)