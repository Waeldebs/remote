from pythonProject7.model.legs import Legs


class PerfLeg(Legs):
    def __init__(self, schedule_generator, basket):
        super().__init__(schedule_generator)
        self.basket = basket

    def get_basket(self):
        return self.basket.gg()

