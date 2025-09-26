from vytek_module import VyTekModule

class VYRALINK(VyTekModule):
    def __init__(self):
        super().__init__("VYRALINK")
        self.shipments = []

    def schedule_shipment(self, origin, destination, payload):
        self.shipments.append({"origin": origin, "destination": destination, "payload": payload})
        print(f"[VYRALINK] Shipment scheduled from {origin} to {destination} carrying {payload}")