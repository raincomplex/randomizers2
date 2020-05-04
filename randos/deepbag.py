'''
one bag is used to fill another, which is drawn from to deal pieces
'''

def factory(name, bag='jiltsoz', windowsize=7):
    class C:
        def __init__(self, rand, state=None):
            self.rand = rand

            if state == None:
                self.bag = list(bag)
                self.bag.sort()

                self.window = []
                for _ in range(windowsize):
                    self.window.append(self.bagnext())
                self.window.sort()

            else:
                self.window = list(state[0])
                self.window.sort()
                self.bag = list(state[1])
                self.bag.sort()

        def getstate(self):
            return (''.join(self.window), ''.join(self.bag))

        def next(self):
            p = self.rand.choice(self.window)
            self.window.remove(p)
            self.window.append(self.bagnext())
            self.window.sort()
            return p

        def bagnext(self):
            p = self.rand.choice(self.bag)
            self.bag.remove(p)
            if not self.bag:
                self.bag = list(bag)
                self.bag.sort()
            return p

    C.__name__ = name
    C.__qualname__ = name
    return C

DeepBag = factory('DeepBag')
