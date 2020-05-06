'script for exploring randomizer states'
import sys, rng, randos, machine

pyrandom = rng.Python()

if len(sys.argv) < 2:
    print('Usage: python3 exploreStates.py RANDOMIZER [STATE_EXPR]')
    print()
    print('Randomizers:')
    for name in sorted(randos.byname):
        print('   ', name)
    exit(1)

Rando = randos.byname[sys.argv[1]]
m = machine.Machine(Rando)

if len(sys.argv) >= 3:
    start = eval(sys.argv[2])
else:
    start = None

seq = ''
while True:
    d = m.getedges(start)
    lst = []
    print('sequence:', seq)
    print('from state', start)
    for (state, piece), prob in d.items():
        lst.append((state, piece, prob))
        print('%3d.  %.5f  %s  %s' % (len(lst), prob, piece, state))
    print()

    try:
        n = input('> ')
    except KeyboardInterrupt:
        break
    except EOFError:
        break

    if n.isdigit():
        n = int(n)

    elif n == '':
        r = pyrandom.random()
        n = 0
        while n < len(lst):
            r -= lst[n][2]
            if r <= 0:
                break
            n += 1
        if n == len(lst):
            n -= 1

    else:
        continue

    start, deal, prob = lst[n]
    seq += deal
