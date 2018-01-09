from collections.abc import Generator
from itertools import islice


class FourGenerator(Generator):

    def __init__(self):
        # iter(range) nejde, 'range_iterator' object has no attribute 'send'
        self._gen_iter = (i for i in range(4))

    def send(self, value):
        # or just next(self._gen_iter), if you're sure you don't care about what value the
        # underlying generator receives
        return self._gen_iter.send(value)

    def throw(self, typ, val=None, tb=None):
        self._gen_iter.throw(typ, val, tb)


fg = FourGenerator()
print(list(islice(fg, 2)))
print(list(islice(fg, 2)))


class PseudoNativeNumberSequenceExtension:

    def __init__(self):
        self._coll = [1, 2, 3, 4, None]

    def get_next(self):
        return self._coll.pop(0)


pnnse = PseudoNativeNumberSequenceExtension()
