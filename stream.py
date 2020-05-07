import os, sys, math, time, pickle, signal
import rng, randos
from subseqcmp import distance, magnitude

unlabeled = True
historySize = 4
stopParam = 100000

pyrandom = rng.Python()

def main():
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
    else:
        cmd = None

    loadstreams()
 
    if cmd == 'run':
        run()

    elif cmd == 'clear':
        del streams[sys.argv[2]]
        savestreams()

    else:
        showinfo()

class Stream:
    def __init__(self, Rando, unlabeled=False):
        self.labeled = not unlabeled
        self.rando = Rando(pyrandom)
        self.trans = {}

        self.history = ''
        for _ in range(100):
            self.history += self.rando.next()
        self.history = self.history[-historySize:]

    def run(self, count):
        if self.labeled:
            for _ in range(count):
                p = self.rando.next()

                if self.history not in self.trans:
                    self.trans[self.history] = {c: 0 for c in 'jiltsoz'}
                self.trans[self.history][p] += 1

                self.history = self.history[1:] + p

        else:
            for _ in range(count):
                p = self.rando.next()

                seen = {}
                h = ''
                for c in self.history:
                    if c not in seen:
                        seen[c] = str(len(seen))
                    h += seen[c]

                if p not in seen:
                    pu = str(len(seen))
                else:
                    pu = seen[p]

                if h not in self.trans:
                    self.trans[h] = {c: 0 for c in '0123456'}
                self.trans[h][pu] += 1

                self.history = self.history[1:] + p

def getdatafilename():
    return 'stream%d%s.pickle' % (historySize, 'u' if unlabeled else '')

def loadstreams():
    global streams
    filename = getdatafilename()
    if os.path.exists(filename + '.backup'):
        os.rename(filename + '.backup', filename)
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            streams = pickle.load(f)
    else:
        streams = {}

def savestreams():
    global streams
    filename = getdatafilename()
    if os.path.exists(filename):
        os.rename(filename, filename + '.backup')
    with open(filename, 'wb') as f:
        pickle.dump(streams, f)
    if os.path.exists(filename + '.backup'):
        os.remove(filename + '.backup')

def run():
    for name, Rando in randos.byname.items():
        if name not in streams:
            streams[name] = Stream(Rando, unlabeled)

    # these values are tweaked dynamically by the loop
    runcount = 1000
    goaltime = 5
    runflag = True

    def sigint_handler(sig, frame):
        nonlocal runflag
        print('stopping...')
        runflag = False
        signal.signal(signal.SIGINT, prevSigHandler)
    prevSigHandler = signal.signal(signal.SIGINT, sigint_handler)

    lastpickle = time.time()
    disabled = set()
    #disabled = set(randos.byname) - {'Balanced', 'DeepBag'}
    #disabled = set(randos.byname) - {'FullRandom', 'FullRandom2'}
    while runflag:

        print('%7s %7s %7s %7s %9s %10s  %s' % ('trans', 'min', 'low', 'med', 'max', 'total', 'name'))
        for name, stream in sorted(streams.items(), key=lambda t: (len(t[1].trans), t[0])):
            counts = [sum(d.values()) for d in stream.trans.values()]
            counts.sort()
            minval = counts[0] if counts else 0
            lowval = counts[7] if len(counts) >= 8 else minval
            medval = counts[int(len(counts) / 2)] if counts else 0
            maxval = counts[-1] if counts else 0
            total = sum(counts)

            if lowval >= stopParam:
                disabled.add(name)

            if name in disabled:
                name = '(%s)' % name
            print('%7d %7d %7d %7d %9d %10d  %s' % (len(stream.trans), minval, lowval, medval, maxval, total, name))
        print()

        t = time.time()
        anyrun = False
        for name, stream in streams.items():
            if name not in disabled:
                stream.run(runcount)
                anyrun = True

        t = time.time() - t
        runcount = int(goaltime * runcount / t)
        print('new runcount', runcount)

        if time.time() - lastpickle >= 60:
            print('pickling...')
            savestreams()
            print()
            lastpickle = time.time()

        print()
        if not anyrun:
            break

    print('pickling...')
    savestreams()

def showinfo():
    '''
    for name, stream in streams.items():
        print(name)
        for context, probs in sorted(stream.trans.items()):
            mag = math.sqrt(sum(v ** 2 for v in probs.values()))
            niceprobs = ' '.join(p + ('%.5f' % (probs[p] / mag)).lstrip('0') for p in 'jiltsoz')
            count = sum(probs.values())
            print('   ', context, niceprobs, mag, count)
        print()
    #'''

    enabled = set()  # everything
    #enabled = {'TGM', 'Bag', 'Constant', 'FullRandom', 'DeepBag', 'Balanced', 'WeightInfinite'}

    # normalize probs
    for name, stream in streams.items():
        for context, probs in stream.trans.items():
            mag = math.sqrt(sum(v ** 2 for v in probs.values()))
            for p in probs:
                probs[p] /= mag

    done = set()
    out = []
    for name, stream in streams.items():
        for name2, stream2 in streams.items():
            if enabled and (name not in enabled or name2 not in enabled):
                continue
            if name == name2:
                continue
            if frozenset((name, name2)) in done:
                continue
            done.add(frozenset((name, name2)))

            lst = []
            for context in set(stream.trans) | set(stream2.trans):
                if context in stream.trans and context in stream2.trans:
                    d = distance(stream.trans[context], stream2.trans[context]) / math.sqrt(2)
                else:
                    d = 1
                lst.append(d)

            #m = magnitude(lst) / math.sqrt(len(lst))
            m = sum(lst) / len(lst)
            out.append((m, name, name2))

    out.sort()
    for mag, name, name2 in out:
        print('%.5f' % mag, name, name2)

if __name__ == '__main__':
    main()
