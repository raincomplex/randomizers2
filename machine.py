'''
extract state machines from normal randomizers

use make() to get a state machine from a randomizer
'''
import math, inspect
from cache import loadcached, savecached

# TODO a version of Machine.fill() which exploits piece-relabeling symmetry to factor the state graph

class Machine:
    def __init__(self, Rando):
        self.rando = Rando
        self.cache = {}  # {state: {(nextstate, dealpiece): probability}}
        self.changed = True
        self.path = '%s.machine' % self.rando.__name__

    def load(self):
        self.cache = loadcached(self.path) or {}
        self.changed = False

    def wantsave(self):
        # don't save machines whose randomizers are hinted 'infiniteStates'
        return self.changed and not getattr(self.rando, 'infiniteStates', False)

    def save(self):
        if self.changed:
            savecached(self.path, self.cache)
            self.changed = False

    def getedges(self, state):
        '''
        get all possible transitions from the given state.
        return {(nextstate, piecedealt): probability}
        '''
        if state in self.cache:
            return self.cache[state]

        edges = {}
        rand = RandProbe()
        while True:
            inst = self.rando(rand, state)
            p = inst.next()
            s = inst.getstate()

            edges[s, p] = edges.get((s, p), 0) + rand.probeProbability()
            if not rand.probeNext():
                break

        self.cache[state] = edges
        self.changed = True
        return edges

    def fill(self):
        '''
        populate the cache with all states reachable from the start state (None)
        - erases anything already in the cache
        - does not work on randomizers with an infinite number of states
        '''
        self.cache = {}
        tovisit = {None}
        while tovisit:
            state = tovisit.pop()
            if state in self.cache:
                continue
            self.cache[state] = self.getedges(state)
            for (s, _) in self.cache[state]:
                if s not in self.cache:
                    tovisit.add(s)
        self.changed = True

class RandProbe:
    'an RNG which allows walking all possible random paths'

    def __init__(self, seed=None):
        'seed is ignored'
        self.types = {}  # {ident: typename}
        self.actions = []
        self.pos = 0

    def probeProbability(self):
        'return the probability of the last probed path'
        p = 1
        for act in self.actions:
            t = self.types[act[0]]
            if t == 'randint':
                p /= (act[1][1] - act[1][0] + 1)
            elif t == 'choice':
                p /= len(act[1])
            elif t == 'shuffle':
                p /= math.factorial(len(act[1]))
            else:
                raise Exception('unknown action')
        return p

    def probeNext(self):
        '''
        move the path to the next one
        return True if there are paths remaining, and False otherwise
        '''
        i = len(self.actions) - 1
        while i >= 0:
            t = self.types[self.actions[i][0]]
            if t == 'randint':
                self.actions[i][2] += 1
                if self.actions[i][2] < self.actions[i][1][1] - self.actions[i][1][0] + 1:
                    break
                self.actions[i][2] = 0
            elif t == 'choice':
                self.actions[i][2] += 1
                if self.actions[i][2] < len(self.actions[i][1]):
                    break
                self.actions[i][2] = 0
            elif t == 'shuffle':
                self.actions[i][2] += 1
                if self.actions[i][2] < math.factorial(len(self.actions[i][1])):
                    break
                self.actions[i][2] = 0
            else:
                raise Exception('unknown action')
            i -= 1

        self.pos = 0
        return (i >= 0)

    def doAction(self, typename, args):
        frame = inspect.currentframe().f_back.f_back
        # line number isn't required here, but makes it easier to debug
        ident = (frame.f_code.co_filename, frame.f_lineno, frame.f_lasti)
        del frame

        if ident not in self.types:
            self.types[ident] = typename

        if self.pos == len(self.actions) or self.actions[self.pos][0] != ident or self.actions[self.pos][1] != args:
            if self.pos < len(self.actions):
                self.actions = self.actions[:self.pos]
            self.actions.append([ident, args, 0])
            r = 0
        else:
            r = self.actions[self.pos][2]

        self.pos += 1
        return r

    def randint(self, a, b):
        assert type(a) == int and type(b) == int
        return a + self.doAction('randint', (a, b))

    def choice(self, seq):
        # this allows seq to be a generator
        seq = tuple(seq)
        return seq[self.doAction('choice', seq)]

    def shuffle(self, seq):
        assert type(seq) == list
        n = self.doAction('shuffle', tuple(seq))
        # use a fixed starting point
        seq.sort()
        # do the shuffle encoded in 'n'
        for i in range(len(seq) - 1):
            k = i + n % (len(seq) - i)
            n //= len(seq) - i
            if k != i:
                seq[i], seq[k] = seq[k], seq[i]
        # shuffle is in-place
        return None
