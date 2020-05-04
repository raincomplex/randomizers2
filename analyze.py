'''
compare behavior of randomizers

see run() for an outline of the algorithm
'''
import math, json, hashlib
import rng, machine
from cache import getcached

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

    print('generating sequences')
    sequences = getcached('sequences', lambda: gensequences(randos))

    shown = set()
    for name, seq in sequences:
        if name not in shown:
            print(name, seq)
            shown.add(name)
    print()

    print('getting state maps of randomizers')
    for Rando in randos:
        m = getStateMap(Rando)
        print(Rando.__name__, len(m))
    print()

    print('testing randomizers against sequences')
    # for each sequence, S
    distances = {}  # running totals for pairs of randomizers
    distcounts = {}  # number of sequences in the running totals
    for seqi, (seqRando, seq) in enumerate(sequences):

        def genprobs():
            # for each randomizer, R
            probs = {}  # P()
            for Rando in randos:
                # find states R can be in after generating S
                possible = possibleStates(Rando, seq)

                # find P(R), the next piece probabilities for R after S
                # if no states were possible, there is no P(R). see below for what happens in this case
                if possible:
                    m = getStateMap(Rando)
                    total = sum(possible.values())
                    nxt = {c: 0 for c in 'jiltsoz'}
                    # these two loops do a couple things at once:
                    # - state-transitions are flattened out of the map, as 'nxt' is grouped by piece dealt
                    # - the deal vectors are weighted by the possible states' weight
                    for state, weight in possible.items():
                        for (_, piece), prob in m[state].items():
                            nxt[piece] += prob * weight / total
                    # this is P(R)
                    probs[Rando] = nxt
            return probs

        # cache probs
        # hash needs to depend on randos and seq
        slug = ','.join(sorted(Rando.__name__ for Rando in randos)) + ':' + seq
        cachefile = 'probs.%s' % hashlib.sha1(slug.encode('utf8')).hexdigest()
        probs = getcached(cachefile, lambda: genprobs())

        # compare the next-piece probabilities of each pair of randomizers
        for i, Rando in enumerate(randos):
            for Rando2 in randos[i+1:]:
                if Rando in probs and Rando2 in probs:
                    dist = compareVectors(probs[Rando], probs[Rando2])
                elif Rando in probs or Rando2 in probs:
                    # one randomizer couldn't generate this sequence. give a distance which is at least 1 (the maximum that compareVectors() returns)
                    # possible good values: 1, 2, 10
                    dist = 1
                else:
                    # neither randomizer could generate this sequence. don't even count it
                    dist = None

                if dist != None:
                    key = frozenset((Rando, Rando2))
                    distances[key] = distances.get(key, 0) + dist
                    distcounts[key] = distcounts.get(key, 0) + 1

        # progress indicator
        print('\r%d/%d' % (seqi+1, len(sequences)), end='')
    print('\r\x1b[K', end='')

    # apply appropriate scale
    for key in distances:
        distances[key] /= distcounts[key]

    # output results

    lst = [(dist, key) for key, dist in distances.items()]
    lst.sort()
    for dist, key in lst:
        print('%.5f  %5d  %s' % (dist, distcounts[key], ' - '.join(Rando.__name__ for Rando in key)))
    print()

    with open('analyze.json', 'w') as f:
        d = {}
        for dist, key in lst:
            d[' - '.join(Rando.__name__ for Rando in key)] = dist
        json.dump(d, f)

def gensequences(randos):
    '''
    generate sequences from the given randomizers
    return [(randomizer_name, seq)]
    '''
    seqsize = 100  # sequence will be 1--2 times this value
    seqlead = 100  # lead will be 1--2 times this value
    seqperrando = 100

    sequences = []
    for Rando in randos:
        for i in range(seqperrando):
            r = Rando(pyrandom)
            for _ in range(int(seqlead * (1 + pyrandom.random()))):
                r.next()
            seq = ''.join(r.next() for _ in range(int(seqsize * (1 + pyrandom.random()))))
            sequences.append((Rando.__name__, seq))

    return sequences

statemapcache = {}

def getStateMap(Rando):
    '''
    return {state: {(nextstate, dealpiece): probability}}
    uses machine.make(Rando) to get the state map.
    safe to call repeatedly because this function uses two caches: one on disk, and one in memory.
    '''
    if Rando not in statemapcache:
        cachefile = '%s.%s.statemap' % (Rando.__module__, Rando.__qualname__)
        statemapcache[Rando] = getcached(cachefile, lambda: machine.make(Rando))
    return statemapcache[Rando]

def possibleStates(Rando, seq):
    '''
    find possible states, as if 'seq' was just generated by the randomizer
    weighted by relative likelihood
    
    return {state: weight}
    '''
    # states = {state: {(nextstate, dealpiece): probability}}
    states = getStateMap(Rando)

    # did a bunch of comparisons between equal weights and random weights. the difference is small
    possible = {state: 1 for state in states}
    #possible = {state: pyrandom.random() for state in states}
    #possible = {state: 1 / pyrandom.randint(1, 1e9) for state in states}

    for p in seq:
        new = {}
        for state, weight in possible.items():
            for (nextstate, piece), prob in states[state].items():
                if piece == p:
                    new[nextstate] = new.get(nextstate, 0) + prob * weight

        # normalize weights and iterate at the same time
        total = sum(new.values())
        possible = {state: prob / total for state, prob in new.items()}
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
    Bag Bag2
    TGM TAP
    '''.split()

    run([randos.byname[name] for name in include])
