Custom Python iterators and generators: when to use which

→ DO THIS AS A JUPYTER NOTEBOOK!

# Quick summary

Implementing an iterator with __iter__? What you actually need may be a
subclass of `collections.abc.Generator` instead.

# Intro

Iterators vs. generators (generator functions vs generator iterators) vs. iterables.

https://docs.python.org/3/glossary.html

Generator-iterator API: https://docs.python.org/3/reference/expressions.html#generator.throw

# Use case

Native extension API which we want to write a Pythonic wrapper for.

Python: Resume an __iter__()-based iterator like a generator

Generators can be resumed:

```python
from itertools import islice

def four_gen_iterfunc():
    yield from range(4)

fg = four_gen_iterfunc()
print(list(islice(fg, 2)))
# prints [0, 1]
print(list(islice(fg, 2)))
# prints [2, 3]
```

But as far as I'm aware, `__iter__()`-based iterators cannot:

```python
class FourIterator:

    def __init__(self):
        def gen():
            
        self._gen_iter = (i for i in range(4))

    def __iter__(self):
        yield from self._gen_iter

fc = FourIterator()
print(list(islice(fc, 2)))
# prints [0, 1]
print(list(islice(fc, 2)))
# prints [0, 1] again, because the iterator is reinitialized
```

Of course, this makes sense when you consider that using such a class in an
iterable context results in a **call** to its `__iter__()` method, i.e. each
use corresponds to a call.

This is confusing because superficially, when used as iterables, the syntax is
the same for both generators and `__iter__()`-iterators (see calls to
`islice()` above).

Can you see any immediate drawbacks to such an approach? Are you aware of any
previous discussions along this line of reasoning that you could point me to?
Thanks!

A similar question: https://stackoverflow.com/questions/46464153/different-behavior-of-consumed-python-generators-depending-on-implementation

Also, props to this answer on SO for pointing me to
`collections.abc.Generator`: https://stackoverflow.com/questions/42983569/how-to-write-a-generator-class

But conceptually, this is a generator:

- should be able to call `next()`
- also, different expectations re: what happens when iteration ends:
  - iterator: can restart by putting in an iterable context
  - generator: will be empty on subsequent attempts to iterate over

Subclass `collections.abc.Generator` instead!

```python
from collections.abc import Generator


class FourGenerator(Generator):

    def __init__(self):
        # iter(range) nejde, 'range_iterator' object has no attribute 'send'
        self._gen_iter = (i for i in range(4))

    def send(self, value):
        # or just next(self._gen_iter), if you're sure you don't care about what value the underlying
        # generator receives
        return self._gen_iter.send(value)

    def throw(self, typ, val=None, tb=None):
        self._gen_iter.throw(typ, val, tb)


fg = FourGenerator()
print(list(islice(fg, 2)))
print(list(islice(fg, 2)))
```
