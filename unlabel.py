
unlabel = {}
relabel = {}

def unlabeler(name):
    def f(func):
        unlabel[name] = func
        return func
    return f

def relabeler(name):
    def f(func):
        relabel[name] = func
        return func
    return f


@unlabeler('TGM')
def _(state):
    if state == None:
        return None, ''

    out = ''
    labels = ''
    for p in state:
        if p not in labels:
            labels += p
        out += str(labels.index(p))
    #for c in 'jiltsoz':
    #    if c not in labels:
    #        labels += c
    return out, labels

@relabeler('TGM')
def _(state, labels):
    if state == None:
        return None

    out = ''
    for n in state:
        out += labels[int(n)]
    return out


@unlabeler('Bag')
def _(state):
    if state == None:
        return None, ''

    out = len(state)
    labels = state
    return out, labels

@relabeler('Bag')
def _(state, labels):
    if state == None:
        return None
    return labels


@unlabeler('WeightInfinite')
def _(state):
    if state == None:
        return None, ''

    out = []
    labels = ''
    for p, n in sorted(state, key=lambda t: t[1]):
        out.append(n)
        labels += p
    return tuple(out), labels

@relabeler('WeightInfinite')
def _(state, labels):
    if state == None:
        return None

    out = []
    for p in 'ijlostz':
        out.append((p, state[labels.index(p)]))
    return tuple(out)


def test():
    print('running tests')
    print()

    teststates = {
        'TGM': ['jilt', 'sooz', 'jttt', 'zzzz'],
        'Bag': ['jiltsoz', 'jilt', 'soz', 'i'],
        'WeightInfinite': [
            (('i', 7), ('j', 2), ('l', 4), ('o', 1), ('s', 5), ('t', 6), ('z', 3)),
            (('i', 4), ('j', 6), ('l', 3), ('o', 1), ('s', 2), ('t', 5), ('z', 10)),
            (('i', 6), ('j', 1), ('l', 4), ('o', 8), ('s', 2), ('t', 11), ('z', 3)),
        ],
    }

    for name in sorted(teststates):
        print(name)
        for state in teststates[name]:
            print('   ', state)
            state2, labels = unlabel[name](state)
            assert set(labels) <= set('jiltsoz')
            state3 = relabel[name](state2, labels)
            assert state == state3, "relabel doesn't match unlabel"
    print()

    print('success!')

if __name__ == '__main__':
    test()
