
class WeightInfinite:
    infiniteStates = True

    def __init__(self, rand, state=None):
        self.rand = rand
        if state == None:
            self.drought = {c: 1 for c in 'jiltsoz'}
        else:
            self.drought = dict(state)

    def getstate(self):
        return tuple(sorted(self.drought.items()))

    def next(self):
        total = 0
        for c in 'jiltsoz':
            total += self.drought[c]
        r = self.rand.randint(1, total)
        for c in 'jiltsoz':
            r -= self.drought[c]
            if r <= 0:
                for p in 'jiltsoz':
                    self.drought[p] += 1
                self.drought[c] = 1
                return c
        raise Exception('impossible')

class WeightFinite:
    def __init__(self, rand, state=None):
        self.rand = rand

        if state == None:
            bag = list('jiltsoz')
            self.rand.shuffle(bag)
            self.drought = {c: i + 1 for i, c in enumerate(bag)}
        else:
            self.drought = dict(state)

    def getstate(self):
        return tuple(sorted(self.drought.items()))

    def next(self):
        total = 0
        for c in 'jiltsoz':
            total += self.drought[c]
        r = self.rand.randint(1, total)
        for c in 'jiltsoz':
            r -= self.drought[c]
            if r <= 0:
                for p in 'jiltsoz':
                    if self.drought[p] < self.drought[c]:
                        self.drought[p] += 1
                self.drought[c] = 1
                return c
        raise Exception('impossible')
