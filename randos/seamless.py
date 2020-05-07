'seamless variations of bag'

def factory(name, count=1):
    class C:
        def __init__(self, rand, state=None):
            self.rand = rand

            if state == None:
                self.history = []
            else:
                self.history = list(state)

        def getstate(self):
            return ''.join(self.history)

        def next(self):
            bag = list('jiltsoz' * count)
            for c in self.history:
                if c in bag:
                    bag.remove(c)
            if not bag:
                bag = 'jiltsoz'

            p = self.rand.choice(bag)
            self.history.insert(0, p)
            if len(self.history) > count * 7:
                self.history.pop()
            return p

    C.__name__ = name
    C.__qualname__ = name
    return C

SeamlessBag = factory('SeamlessBag')
SeamlessBag2 = factory('SeamlessBag2', 2)
SeamlessBag3 = factory('SeamlessBag3', 3)
