
class FlatBag:
    'a constant sequence repeating forever'

    sequence = 'jiltsoz'

    def __init__(self, rand, state=None):
        if state == None:
            self.i = rand.randint(0, len(self.sequence) - 1)
        else:
            assert 0 <= state < len(self.sequence)
            self.i = state

    def getstate(self):
        return self.i

    def next(self):
        self.i = (self.i + 1) % len(self.sequence)
        return self.sequence[self.i]

class Metronome:
    'deal an I every 7 pieces, and everything else is random non-I pieces'

    def __init__(self, rand, state=None):
        self.rand = rand
        if state == None:
            self.i = self.rand.randint(0, 6)
        else:
            self.i = state

    def getstate(self):
        return self.i

    def next(self):
        if self.i == 6:
            self.i = 0
            return 'i'
        self.i += 1
        return self.rand.choice('jltsoz')

class FlipFlop:
    'alternating between two subsets of pieces'

    def __init__(self, rand, state=None):
        self.rand = rand
        if state == None:
            self.i = 0
        else:
            self.i = state

    def getstate(self):
        return self.i

    def next(self):
        if self.i == 0:
            if self.rand.randint(0, 3) == 0:
                self.i = 1
            return self.rand.choice('jlti')
        else:
            if self.rand.randint(0, 3) == 0:
                self.i = 0
            return self.rand.choice('sozi')

class RepeatLast:
    'high chance of repeating the piece that was last dealt'

    def __init__(self, rand, state=None):
        self.rand = rand
        self.last = state

    def getstate(self):
        return self.last

    def next(self):
        if self.last == None or self.rand.randint(1, 3) == 1:
            self.last = self.rand.choice('jiltsoz')
        return self.last
