from vytek_module import VyTekModule

class AFRICON(VyTekModule):
    def __init__(self):
        super().__init__("AFRICON")
        self.infrastructure_projects = {}

    def start_project(self, project_id, description):
        self.infrastructure_projects[project_id] = description
        print(f"[AFRICON] Infrastructure project started: {project_id}")