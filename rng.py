'''
objects which generate random numbers

interface RNG:
    def __init__(seed=None)
    def seed(seed)
    def random(): return <float [0..1)>
    def randint(a, b): return <int [a..b]>
    def choice(seq): return <x in seq>
    def sample(seq, n): return [<unique x in seq>]  # with len n
    def shuffle(seq)  # in-place
'''
import time, random

class Python(random.Random):
    "python's mersenne twister"

class Simple:
    '''
    an abstract RNG for producing integers within some size range

    implement seed() and read()
    the rest of the RNG interface is implemented for you based on calls to read()
    '''

    size = 0xffffffff
    def __init__(self, seed=None):
        if seed == None:
            seed = int(time.time())
        self.seed(seed)

    def seed(self, seed):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def random(self):
        return self.read() / self.size

    def randint(self, a, b):
        return a + self.read() % (b - a + 1)

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]

    def sample(self, seq, n):
        assert n <= len(seq)
        opts = list(seq)
        r = []
        for _ in range(n):
            i = self.randint(0, len(opts) - 1)
            r.append(opts[i])
            del opts[i]
        return r

    def shuffle(self, seq):
        for i in range(len(seq) - 1):
            k = self.randint(i, len(seq) - 1)
            if i != k:
                seq[i], seq[k] = seq[k], seq[i]
        return None
