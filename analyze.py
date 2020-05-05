'''
compare behavior of randomizers

see run() for an outline of the algorithm
'''
import math, json, hashlib, profile
import rng, machine
from cache import getcached, loadcached, savecached

seqSize = 100  # sequence will be 1--2 times this value
seqLead = 100  # lead will be 1--2 times this value
seqPerRando = 100  # total sequences will be this * len(randos)

profileRandomizer = None  # set to randomizer name or None
useSequenceCache = True

pyrandom = rng.Python()

def run(randos):
    '''
    start running totals for each unique pair of randomizers (R1, R2)
    
    for each random piece sequence, S:
        for each randomizer, R:
            - find the states R could be in after generating S, weighted relative to each other
            - for each state, find the probabilities of next pieces
            - sum the next piece probabilities, weighted by state
            * you now have P(R), a single vector of piece probabilities for R after S
        for every unique pair of randomizers R1, R2:
            - add the distance between P(R1) and P(R2) to the running total for (R1, R2)
            * in other words, compare the next-piece probabilities of the two randomizers
    
    at the end, the running totals for (R1, R2) are a measurement of how different the behaviors of the two randomizers are. a lower number means 'more similar'.
    '''

    print('getting sequences')
    if useSequenceCache:
        sequences = []
        for Rando in randos:
            cachefile = '%s.sequences' % Rando.__name__
            sequences += getcached(cachefile, lambda: gensequences([Rando]))
    else:
        sequences = gensequences(randos)

    count = {}
    for name, seq in sequences:
        c, ex = count.get(name, (0, ''))
        count[name] = (c + 1, seq)
    for name, (num, seq) in count.items():
        print(num, name, seq)
    print()

    machines = {Rando: machine.Machine(Rando) for Rando in randos}
    for mach in machines.values():
        print('loading machine', mach.rando.__name__)
        mach.load()
    print()

    print('testing randomizers against sequences')

    distances = {}  # {<frozenset rando pair>: [distance]}
    probscache = ProbsCache()

    # for each sequence, S
    for seqi, (seqRando, seq) in enumerate(sequences):

        def progress(msg=''):
            print('\r%d/%d %s\x1b[K' % (seqi+1, len(sequences), msg), end='')

        progress()

        # for each randomizer, R
        probs = {}  # P()
        for Rando in randos:
            progress(Rando.__name__)
            # find P(R), the next piece probabilities for R after S
            if Rando.__name__ == profileRandomizer:
                profile.runctx('probs[Rando] = probscache.get(machines[Rando], seq)', {
                    'probs': probs,
                    'Rando': Rando,
                    'probscache': probscache,
                    'machines': machines,
                    'seq': seq,
                }, {})
            else:
                probs[Rando] = probscache.get(machines[Rando], seq)

        # compare the next-piece probabilities of each pair of randomizers
        for i, Rando in enumerate(randos):
            for Rando2 in randos[i+1:]:
                if probs[Rando] and probs[Rando2]:
                    dist = compareVectors(probs[Rando], probs[Rando2])
                elif probs[Rando] or probs[Rando2]:
                    # one randomizer couldn't generate this sequence. give a distance which is at least 1 (the maximum that compareVectors() returns)
                    # possible good values: 1, 2, 10
                    dist = 1
                else:
                    # neither randomizer could generate this sequence. don't even count it
                    dist = None

                if dist != None:
                    key = frozenset((Rando, Rando2))
                    if key not in distances:
                        distances[key] = []
                    distances[key].append(dist)

    print('\r\x1b[K')

    # save changed data
    anysaved = False

    if probscache.changed:
        print('saving probs cache')
        probscache.save()
        anysaved = True

    for mach in machines.values():
        if mach.wantsave():
            print('saving machine', mach.rando.__name__)
            mach.save()
            anysaved = True

    if anysaved:
        print()

    # output results

    lst = [(sum(points) / len(points), len(points), key) for key, points in distances.items()]
    lst.sort()
    print('%7s  %5s  %s' % ('avgdist', 'count', 'randomizer pair'))
    for avg, count, key in lst:
        key = ' - '.join(Rando.__name__ for Rando in key)
        print('%.5f  %5d  %s' % (avg, count, key))
    print()

    with open('analyze.json', 'w') as f:
        d = {}
        for key, points in distances.items():
            key = ' - '.join(Rando.__name__ for Rando in key)
            d[key] = points
        json.dump(d, f)

def gensequences(randos):
    '''
    generate sequences from the given randomizers
    return [(randomizer_name, seq)]
    '''
    sequences = []
    for Rando in randos:
        for i in range(seqPerRando):
            r = Rando(pyrandom)
            for _ in range(int(seqLead * (1 + pyrandom.random()))):
                r.next()
            seq = ''.join(r.next() for _ in range(int(seqSize * (1 + pyrandom.random()))))
            sequences.append((Rando.__name__, seq))

    return sequences

class ProbsCache:
    'cache probs vector, keyed by (Rando, seq)'

    def __init__(self):
        self.cache = loadcached('probs') or {}
        self.changed = False

    def get(self, mach, seq):
        key = '%s:%s' % (mach.rando.__name__, seq)
        key = hashlib.sha1(key.encode('utf8')).digest()
        if key not in self.cache:
            self.cache[key] = calcProbsAfter(mach, seq)
            self.changed = True
        return self.cache[key]

    def save(self):
        if self.changed:
            savecached('probs', self.cache)
            self.changed = False

def calcProbsAfter(mach, seq):
    'calculate the next-piece probabilities for Rando after it has just output seq'

    # find states R can be in after generating S
    possible = possibleStates(mach, seq)

    # if no states were possible, there is no P(R). see 'compare' loops below for what happens in this case
    if not possible:
        return None

    total = sum(possible.values())
    nxt = {c: 0 for c in 'jiltsoz'}
    # these two loops do a couple things at once:
    # - state-transitions are flattened out of the map, as 'nxt' is grouped by piece dealt
    # - the deal vectors are weighted by the possible states' weight
    for state, weight in possible.items():
        for (_, piece), prob in mach.getedges(state).items():
            nxt[piece] += prob * weight / total
    return nxt

def possibleStates(mach, seq):
    '''
    find possible states, as if 'seq' was just generated by the randomizer
    weighted by relative likelihood
    
    return {state: weight}
    '''

    def iterate(piece):
        nonlocal possible
        new = {}
        for state, weight in possible.items():
            for (nextstate, p), prob in mach.getedges(state).items():
                if not piece or p == piece:
                    new[nextstate] = new.get(nextstate, 0) + prob * weight

        # normalize weights and update 'possible' at the same time
        total = sum(new.values())
        possible = {state: prob / total for state, prob in new.items()}

    # starting from the initial state, find at least one state that can deal the first piece of the sequence
    possible = {None: 1}
    candeal = False
    while not candeal:
        for state in possible:
            for (s, p) in mach.getedges(state):
                if p == seq[0]:
                    candeal = True

        if not candeal:
            iterate(None)

    for p in seq:
        iterate(p)
        if not possible:
            break

    return possible

def compareVectors(a, b):
    '''
    takes two normalized 7-vectors (with keys in 'jiltsoz')
    return <float 0..1>
    where 0 is identical and 1 is maximally different (although perhaps not uniquely)
    '''
    # FIXME calculate angular distance instead of straight-line
    # calculate distance between the two vectors
    total = 0
    for c in 'jiltsoz':
        total += (a[c] - b[c]) ** 2
    # maximum distance between two normalized N-dimensional vectors with non-negative components is sqrt(2)
    return math.sqrt(total) / math.sqrt(2)


if __name__ == '__main__':
    import randos

    include = '''
    FullRandom
    FlatBag Metronome FlipFlop RepeatLast
    NES
    Bag Bag2 DeepBag Balanced
    TGM TAP
    WeightFinite WeightInfinite
    '''.split()

    # remove 'commented' randomizers
    include = [name for name in include if not name.startswith('#')]

    run([randos.byname[name] for name in include])
