from vytek_module import VyTekModule

class GROVES_STREET_CAPITAL_PARTNERS(VyTekModule):
    def __init__(self):
        super().__init__("GROVES STREET CAPITAL PARTNERS")
        self.investments = {}

    def invest(self, project_id, amount):
        self.investments[project_id] = self.investments.get(project_id, 0) + amount
        print(f"[GSC] Invested {amount} in {project_id}")