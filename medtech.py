from vytek_module import VyTekModule

class MedTech(VyTekModule):
    def __init__(self):
        super().__init__("MedTech")
        self.patient_data = {}

    def add_patient_record(self, patient_id, record):
        self.patient_data[patient_id] = record
        print(f"[MedTech] Record added for patient {patient_id}")