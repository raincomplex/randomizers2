'utility module for caching objects to disk'
import os, time, glob, pickle

if not os.path.isdir('cache'):
    os.mkdir('cache')

# TODO persist this in the cache
usedcache = {}

def getcached(filename, valuefunc):
    'load a pickled value from "cache/$filename", or compute it with valuefunc() and save it'
    usedcache[filename] = time.time()
    filename = os.path.join('cache', filename)
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        value = valuefunc()
        with open(filename, 'wb') as f:
            pickle.dump(value, f)
        return value

# TODO delete old cache files
'''
def cleancache():
    for fn in glob.glob('cache/*'):
        fn = fn.split('/')[-1]
'''
