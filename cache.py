'utility module for caching objects to disk'
import os, time, glob, pickle

if not os.path.isdir('cache'):
    os.mkdir('cache')

usedfile = os.path.join('cache', 'used-log')
if os.path.exists(usedfile):
    with open(usedfile, 'rb') as f:
        usedcache = pickle.load(f)
else:
    usedcache = {}

def saveusedcache():
    with open(usedfile, 'wb') as f:
        pickle.dump(usedcache, f)

def getcached(filename, valuefunc):
    'load a pickled value from "cache/$filename", or compute it with valuefunc() and save it'
    assert '/' not in filename and '\\' not in filename, 'no slashes allowed in filename'
    value = loadcached(filename)
    if value == None:
        value = valuefunc()
        savecached(filename, value)
    return value

def loadcached(filename):
    'return cached value or None if no value is cached'
    assert '/' not in filename and '\\' not in filename, 'no slashes allowed in filename'
    usedcache[filename] = time.time()
    saveusedcache()

    filename = os.path.join('cache', filename)
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None

def savecached(filename, value):
    'write value to cache'
    assert '/' not in filename and '\\' not in filename, 'no slashes allowed in filename'
    usedcache[filename] = time.time()
    saveusedcache()

    filename = os.path.join('cache', filename)
    with open(filename, 'wb') as f:
        pickle.dump(value, f)

def cleancache(delta):
    "delete cache files that haven't been loaded or saved in at least 'delta' seconds"
    for fn in glob.glob(os.path.join('cache', '*')):
        fn = fn.split('/')[-1]
        if fn in usedcache and time.time() - usedcache[fn] >= delta:
            os.remove(os.path.join('cache', fn))
            del usedcache[fn]
    saveusedcache()
