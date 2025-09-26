from vytek_module import VyTekModule

class STREAMLINE(VyTekModule):
    def __init__(self):
        super().__init__("STREAMLINE")
        self.creators = {}

    def onboard_creator(self, creator_id, profile):
        self.creators[creator_id] = profile
        print(f"[STREAMLINE] Creator onboarded: {creator_id}")