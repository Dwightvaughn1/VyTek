from vytek_module import VyTekModule

class EAGLE_EYE(VyTekModule):
    def __init__(self):
        super().__init__("EAGLE EYE")
        self.surveillance_log = []

    def record_sight(self, location, event):
        self.surveillance_log.append((location, event))
        print(f"[EAGLE EYE] Recorded event at {location}: {event}")