import random


class AlphaClass:
    def __init__(self, randomlist=None, lowerlimit=None, upperlimit=None):
        self.list = [1, 2, 3, 4, 5] if not randomlist else randomlist
        self.lowerlimit = 0 if not lowerlimit else lowerlimit
        self.upperlimit = 100 if not upperlimit else upperlimit

    def random_number(self):
        return random.randint(self.lowerlimit, self.upperlimit)

    def random_choice(self):
        return random.choice(self.list)

    def random_sample(self):
        return random.sample(self.list, 3)
