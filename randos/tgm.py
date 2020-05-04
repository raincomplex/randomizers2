import rng

pieces = 'izsjlot'

def factory(name, rolls, start):
    assert type(start) == str and len(start) == 4

    class C:
        def __init__(self, rand, state=None):
            self.rand = rand

            if state == None:
                #b = 'z'
                #while b == 'z' or b == 's' or b == 'o':
                #    b = pieces[self.rand.randint(0, 6)]
                b = self.rand.choice('jilt')
                self.history = b + start[:3]

            else:
                assert type(state) == str and len(state) == 4
                self.history = state

        def getstate(self):
            return self.history

        def next(self):
            r = self.history[0]

            for i in range(rolls - 1):
                b = pieces[self.rand.randint(0, 6)]
                if b not in self.history:
                    break
                #self.rand.randint(0, 6)

            self.history = b + self.history[:3]
            return r

    C.__name__ = name
    C.__qualname__ = name
    return C

TGM = factory('TGM', 4, 'zzzz')
TAP = factory('TAP', 6, 'szsz')


class TGM_RNG(rng.Simple):
    size = 0x8000

    def seed(self, seed):
        self.state = seed

    def read(self):
        self.state = (self.state * 0x41c64e6d + 12345) & 0xffffffff
        return (self.state >> 10) & 0x7fff

    def unread(self):
        self.state = ((self.state - 12345) * 0xeeb9eb65) & 0xffffffff
