'failure modes of machine.make()'
import machine

class InfinitePath:
    '''
    locks up RandProbe on randomizer instantiation in machine.getedges(), because rand.choice() always returns 0 the first time it's called

    solution: don't write loops like this
    '''

    def __init__(self, rand, state=None):
        x = 'a'
        while x == 'a':
            x = rand.choice('ab')
        # maybe could get out with an action stack limit that starts returning actual random values?

    def getstate(self):
        return None

    def next(self):
        return 'a'

class InfinitePath2:
    '''
    locks up RandProbe on randomizer instantiation in machine.getedges(), because rand.choice() can always provide a way for the while loop to continue
    
    one solution: a probability threshold in getedges()
    better solution: don't write loops like this
    '''

    def __init__(self, rand, state=None):
        x = 'b'
        while x == 'b':
            x = rand.choice('ab')

    def getstate(self):
        return None

    def next(self):
        return 'a'

class InfiniteStates:
    'locks up make() in finding new states, because they are infinite'

    def __init__(self, rand, state=None):
        self.rand = rand
        self.i = state or 0

    def getstate(self):
        return self.i

    def next(self):
        if self.rand.randint(0, 1):
            self.i = 0
            return 'a'
        else:
            self.i += 1
            return 'b'


import randos

#m = machine.make(InfiniteStates)
#m = machine.make(randos.TGM)
#m = machine.make(randos.DeepBag)
m = machine.make(randos.WeightFinite)

if len(m) < 150:
    for state, trans in m.items():
        print(state, '->', trans)
print('num states =', len(m))
