from vytek_module import VyTekModule

class SMART_GOV_360(VyTekModule):
    def __init__(self):
        super().__init__("SMART-GOV 360")
        self.citizen_registry = {}
        self.votes = {}

    def register_citizen(self, citizen_id, user_name):
        self.citizen_registry[citizen_id] = user_name
        print(f"[SMART-GOV 360] Registered citizen {user_name} ({citizen_id})")

    def cast_vote(self, citizen_id, proposal_id, vote):
        if citizen_id not in self.citizen_registry:
            print(f"[SMART-GOV 360] Citizen {citizen_id} not registered.")
            return False
        self.votes.setdefault(proposal_id, {})
        self.votes[proposal_id][citizen_id] = vote
        print(f"[SMART-GOV 360] Citizen {citizen_id} voted {vote} on proposal {proposal_id}")
        return True