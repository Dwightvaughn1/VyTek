from vytek_module import VyTekModule

class VYRALERT(VyTekModule):
    def __init__(self):
        super().__init__("VYRALERT")
        self.incidents = []

    def report_incident(self, incident_type, severity):
        self.incidents.append({"type": incident_type, "severity": severity})
        print(f"[VYRALERT] Incident reported: {incident_type}, severity: {severity}")