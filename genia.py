from vytek_module import VyTekModule

class GENIUS(VyTekModule):
    def __init__(self):
        super().__init__("GENIUS")
        self.curriculum = {}

    def add_course(self, course_id, details):
        self.curriculum[course_id] = details
        print(f"[GENIUS] Course added: {course_id}")