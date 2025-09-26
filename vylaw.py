from vytek_module import VyTekModule

class VyLaw(VyTekModule):
    def __init__(self):
        super().__init__("VyLaw")
        self.contract_registry = {}

    def register_contract(self, contract_id, details):
        self.contract_registry[contract_id] = details
        print(f"[VyLaw] Contract registered: {contract_id}")

    def check_compliance(self, contract_id):
        compliance = contract_id in self.contract_registry
        print(f"[VyLaw] Compliance check for {contract_id}: {compliance}")
        return compliance