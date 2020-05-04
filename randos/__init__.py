'''
module containing randomizer implementations

interface Randomizer:
    # NB: randomizers do not inherit from anything. they are ducktyped to this interface

    def __init__(self, rand, state=None):
        # NB: it should always be true that: Randomizer(rand, state).getstate() == state
        # EXCEPT for state == None, which means "choose your own starting state" (can use rand)

        # NB: randomizers should use the supplied 'rand' instead of any other way of generating random numbers. see rng.py for details on the 'rand' object
        pass

    def getstate(self):
        # NB: states should be immutable
        return <state>

    def next(self):
        return <piece>

Randomizer classes in randos/*.py are imported into the top level of this module. They are also available in the 'byname' dict.
'''
import re, glob, importlib

modules = {}
byname = {}

def _init():
    # fill modules
    for name in glob.glob('randos/*.py'):
        if name.endswith('/__init__.py'):
            continue
        name = re.sub(r'randos/(.*)\.py$', lambda m: m.group(1), name)
        modules[name] = importlib.import_module('randos.' + name)

    # fill byname, set globals
    for name, m in sorted(modules.items()):
        found = 0
        for rname in dir(m):
            obj = getattr(m, rname)
            if type(obj) == type and hasattr(obj, 'getstate') and hasattr(obj, 'next'):
                if rname in byname:
                    raise Exception('duplicate name %r' % rname)
                byname[rname] = obj
                globals()[rname] = obj
                found += 1
        if found == 0:
            print('found no randomizers in module:', name)

_init()
