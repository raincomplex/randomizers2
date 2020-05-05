'a tool to print and compare the json files output by analyze.py'
import sys, json, math

def main():
    cmd = sys.argv.pop(0)
    if len(sys.argv) == 2:
        f1, f2 = sys.argv
    elif len(sys.argv) == 1:
        f1, = sys.argv
        f2 = None
    else:
        print('Usage: %s JSON [JSON]' % cmd)
        exit(1)

    with open(f1, 'r') as f:
        f1data = json.load(f)

    if not f2:
        lst = [(sum(points) / len(points), key) for key, points in f1data.items()]
        lst.sort()
        for n, key in lst:
            print('%.5f  %s' % (n, key))

    else:
        with open(f2, 'r') as f:
            f2data = json.load(f)

        lst = []
        for key in set(f1data) | set(f2data):
            if key in f1data and key in f2data:
                avg1 = sum(f1data[key]) / len(f1data[key])
                avg2 = sum(f2data[key]) / len(f2data[key])
                lst.append((avg2 - avg1, key, ''))
            else:
                lst.append((math.inf, key, 'only in %s' % (f1 if key in f1data else f2)))

        lst.sort()

        for diff, key, msg in lst:
            print(diff, key, msg)

if __name__ == '__main__':
    main()
