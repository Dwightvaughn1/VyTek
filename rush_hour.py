from vytek_module import VyTekModule

class RUSH_HOUR(VyTekModule):
    def __init__(self):
        super().__init__("RUSH-HOUR")
        self.requests = []

    def send_assistance(self, location, type_of_help):
        self.requests.append({"location": location, "type": type_of_help})
        print(f"[RUSH-HOUR] Assistance sent to {location} for {type_of_help}")