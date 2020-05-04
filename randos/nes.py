
class NES:
    def __init__(self, rand, state=None):
        self.rand = rand
        self.last = state

    def getstate(self):
        return self.last

    def next(self):
        p = self.rand.choice('jiltsozx')
        if p == 'x' or p == self.last:
            p = self.rand.choice('jiltsoz')
        self.last = p
        return p
