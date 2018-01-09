def genfunc():
    for i in range(10):
        print(f"genfunc: yielding {i}")
        yield i


gen = genfunc()


def wrapper():
    yield from gen


wrapped_gen = wrapper()
print("toplevel:", next(gen), "from gen")
print("toplevel:", next(iter(wrapped_gen)), "from wrapped_gen")
print("toplevel:", next(gen), "from gen")
print("toplevel:", next(iter(wrapped_gen)), "from wrapped_gen")
# → iteration can alternate between gen and wrapped_gen

print()

gen = genfunc()
print("toplevel:", next(gen), "from gen")
print("toplevel:", next(iter(wrapper())), "from wrapper()")
try:
    print(next(gen))
except StopIteration:
    print("toplevel: can't call next(gen) anymore")
try:
    print(next(iter(wrapper())))
except StopIteration:
    print("toplevel: can't call next(iter(wrapper())) anymore either")
# → once wrapper() is called once, the rest of the iterator is in limbo (?)

###############################################################################

from itertools import islice


def four_genfunc():
    yield from range(4)


fg = four_genfunc()
print(list(islice(fg, 2)))
print(list(islice(fg, 2)))


class FourIterator:

    def __init__(self):

        def gen():
            yield from range(4)

        self._gen = gen()

    def __iter__(self):
        yield from self._gen


fc = FourIterator()
print(list(islice(fc, 2)))
print(list(islice(fc, 2)))


class FourIterator:

    def __iter__(self):
        yield from range(4)


fc = FourIterator()
print(list(islice(fc, 2)))
print(list(islice(fc, 2)))
