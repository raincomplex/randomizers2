
class FullRandom:
    def __init__(self, rand, state=None):
        self.rand = rand

    def getstate(self):
        return None

    def next(self):
        return self.rand.choice('jiltsoz')

class FullRandom2:
    '''
    pick a random 2-gram
    (identical behavior to FullRandom but uses more states)
    '''

    def __init__(self, rand, state=None):
        self.rand = rand
        self.state = state

    def getstate(self):
        return self.state

    def next(self):
        if self.state == None:
            self.state = self.rand.choice('jiltsoz')
            return self.rand.choice('jiltsoz')
        p = self.state
        self.state = None
        return p
