from vytek_module import VyTekModule

class OBLiGATE(VyTekModule):
    def __init__(self):
        super().__init__("OBLiGATE")
        self.policies = {}

    def issue_policy(self, policy_id, coverage_amount):
        self.policies[policy_id] = coverage_amount
        print(f"[OBLiGATE] Policy issued: {policy_id}, coverage: {coverage_amount}")