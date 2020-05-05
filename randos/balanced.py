'based on <a href="https://www.reddit.com/r/Tetris/comments/ceap8l/randomizer_concept_ramblings/">this reddit post</a>'
import math

def factory(name, frombag=5, fromrand=2, fromfreq=2):
    class C:
        'make bags by taking a number of pieces from a standard bag, random, and least frequency'

        infiniteStates = True

        def __init__(self, rand, state=None):
            self.rand = rand

            if state == None:
                self.counts = {c: 0 for c in 'jiltsoz'}
                self.metabag = []
                self.bag = []

            else:
                self.counts = {c: n for c, n in zip('jiltsoz', state[0])}
                self.metabag = list(state[1])
                self.bag = list(state[2])

        def getstate(self):
            return (
                tuple(self.counts[c] for c in 'jiltsoz'),
                ''.join(sorted(self.metabag)),
                ''.join(sorted(self.bag)),
            )

        def next(self):
            if not self.metabag:
                self.metabag = list('b' * frombag + 'r' * fromrand + 'f' * fromfreq)

            t = self.rand.choice(self.metabag)
            self.metabag.remove(t)

            if t == 'b':
                if not self.bag:
                    self.bag = list('jiltsoz' * math.ceil(frombag / 7))
                p = self.rand.choice(self.bag)
                self.bag.remove(p)

            elif t == 'r':
                p = self.rand.choice('jiltsoz')

            elif t == 'f':
                low = [c for c in self.counts if self.counts[c] == 0]
                p = self.rand.choice(low)

            else:
                raise ValueError('impossible')

            self.countpiece(p)
            return p

        def countpiece(self, p):
            self.counts[p] += 1
            if 0 not in self.counts.values():
                for c in 'jiltsoz':
                    self.counts[c] -= 1

    C.__name__ = name
    C.__qualname__ = name
    return C

Balanced = factory('Balanced')
