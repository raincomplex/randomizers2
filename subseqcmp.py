'measure similarity of sequences by comparing subsequence counts'
import rng
from collections import Counter

def run(randos):
    seqsize = 1000
    seqlead = 100
    seqperrando = 50

    searchsize = 6

    print('generating sequences')
    sequences = []
    for Rando in randos:
        print(Rando)
        for _ in range(seqperrando):
            r = Rando(rng.Python())
            for i in range(seqlead):
                r.next()
            seq = ''.join(r.next() for _ in range(seqsize))
            sequences.append((Rando, seq))
    print()

    print('counting sequences')
    counted = {}
    for _, seq in sequences:
        c = Counter()
        for i in range(len(seq) - searchsize + 1):
            search = seq[i:i+searchsize]
            c[search] += 1
        counted[seq] = c
    print()

    print('comparing sequences')
    results = {}
    for Rando, seq in sequences:
        for Rando2, seq2 in sequences:
            if seq == seq2:
                continue
            hits = 0
            for i in range(len(seq) - searchsize + 1):
                search = seq[i:i+searchsize]
                hits += counted[seq2][search]
                #hits += seq2.count(search) #/ (len(seq2) - searchsize + 1)
            #hits /= len(seq) - searchsize + 1
            
            key = frozenset((Rando, Rando2))
            if key not in results:
                results[key] = hits
            else:
                results[key] += hits

    for key, hits in sorted(results.items(), key=lambda t: t[1]):
        print(hits, key)

if __name__ == '__main__':
    import randos
    run([randos.FullRandom, randos.NES, randos.Bag, randos.TGM])
