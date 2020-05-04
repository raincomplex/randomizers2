
def factory(name, start):
    class C:
        def __init__(self, rand, state=None):
            self.rand = rand
            if state == None:
                state = start
            self.bag = state

        def getstate(self):
            return self.bag

        def next(self):
            p = self.rand.choice(self.bag)
            i = self.bag.index(p)
            self.bag = self.bag[:i] + self.bag[i+1:]
            if not self.bag:
                self.bag = start
            return p

    C.__name__ = name
    C.__qualname__ = name
    return C

Bag = factory('Bag', 'jiltsoz')

# it's important that identical pieces are adjacent, otherwise there are more possible states
Bag2 = factory('Bag2', 'jjiillttssoozz')
Bag3 = factory('Bag3', 'jjjiiillltttsssooozzz')
Bag4 = factory('Bag4', 'jjjjiiiillllttttssssoooozzzz')
