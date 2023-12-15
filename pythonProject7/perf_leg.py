from legs import Legs

class PerfLeg(Legs):
    def __init__(self, schedule_generator):
        super().__init__(schedule_generator)
