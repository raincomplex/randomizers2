import json

with open('weights-equal.json', 'r') as f:
    equal = json.load(f)

with open('weights-random.json', 'r') as f:
    random = json.load(f)

assert set(equal.keys()) == set(random.keys())

lst = [(equal[key] - random[key], key) for key in equal]
lst.sort()

for diff, key in lst:
    print(diff, key)
