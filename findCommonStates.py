'script to find common states. will also unlabel states if there is an unlabeler for the randomizer.'
import sys, time
import rng, randos, machine, unlabel

pyrandom = rng.Python()

if len(sys.argv) < 2:
    print('Usage: python3 findCommonStates.py RANDOMIZER')
    print()
    print('Randomizers:')
    for name in sorted(randos.byname):
        print('   ', name)
    exit(1)

Rando = randos.byname[sys.argv[1]]
m = machine.Machine(Rando)

unlabelStates = Rando.__name__ in unlabel.unlabel
state = None
count = {}
total = 0

t = time.time()
while True:
    count[state] = count.get(state, 0) + 1
    total += 1

    trans = m.getedges(state)

    r = pyrandom.random()
    for (nextstate, piece), prob in trans.items():
        r -= prob
        if r <= 0:
            state = nextstate
            break

    if total % 1000 == 0 and time.time() - t >= .5:
        t = time.time()
        for s, n in sorted(count.items(), key=lambda t: t[1])[-30:]:
            print('%.10f  %s' % (n / total, s))
        print('total', total)
        print()

        if unlabelStates:
            unlabeled = {}
            func = unlabel.unlabel[Rando.__name__]
            for s, n in count.items():
                key, _ = func(s)
                unlabeled[key] = unlabeled.get(key, 0) + n
            print('unlabeled')
            for s, n in sorted(unlabeled.items(), key=lambda t: t[1])[-30:]:
                print('%.10f  %s' % (n / total, s))
            print('total', total)
            print()
