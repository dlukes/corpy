=====================================
Utility functions for interactive use
=====================================

The :mod:`corpy.util` module is a collection of small utility functions I
occasionally find useful, especially when teaching. They're mostly meant for use
in an interactive session (JupyterLab / IPython), some can even be used as
`IPython magic commands <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__
(remember to run ``%load_ext corpy`` first). Here are some hints explaining when
and why you might want them.

Running code in a sanitized global environment with :func:`corpy.util.clean_env`
================================================================================

When working in a Jupyter notebook, you often end up creating a lot of global
variables while experimenting. Some of them might even end up disappearing from
the written record, as you edit and delete cells. This (partially) invisible
global state accumulates and can lead to hard to debug problems, where typos
pass silently, code mysteriously fails because builtin functions have been
overwritten, etc.

Global variables can hide typos
-------------------------------

For instance, say you're trying to sort numbers. You define a list of numbers
called ``numbers``, try the ``sorted`` function, which seems to work, so you
proceed to write your own wrapper function, ``sort_numbers``. (In real life, the
functionality would obviously be something more involved, to justify writing a
wrapper.)

.. code:: python

    >>> numbers = [0, 3, 1, 2, 4]
    >>> sorted(numbers)
    [0, 1, 2, 3, 4]
    >>> #                ↓ typo!
    >>> def sort_numbers(numbrs):
    ...     return sorted(numbers)
    ...

But in doing so, whoops! You make a typo. You name the function's argument
``numbrs`` without an ``e``, but the variable name you access in the function's
body is ``numbers`` *with* an ``e``. Since there's no local variable called
``numbers`` in the function, it would normally fail with a ``NameError``. But
remember that we've previously defined a global with that same exact name as
part of our interactive experimentation prior to writing the function. So
instead of the typo leading to an error, the name will be resolved in the global
scope.

The tricky thing is, if you only test your function with your previously defined
``numbers`` variable, everything will seem to work fine -- by accident:

.. code:: python

    >>> sort_numbers(numbers)
    [0, 1, 2, 3, 4]

The problem only reveals itself when using another list as input -- you get back
the sorted version of ``numbers`` again:

.. code:: python

    >>> sort_numbers([0, 2, 1])
    [0, 1, 2, 3, 4]

Now, what :func:`corpy.util.clean_env` does is to provide a context manager
which runs a block of code in a sanitized global environment, as a way to
temporarily pretend that (most of) your interactive experimentation (a.k.a.
polluting the global environment) didn't happen. Running the same code under the
context manager yields the expected ``NameError``, which helpfully points to a
problem with our code:

.. code:: python

    >>> from corpy.util import clean_env
    >>> with clean_env():
    ...     sort_numbers([0, 2, 1])
    ...
    Traceback (most recent call last):
      File ..., line 2, in <module>
        sort_numbers([0, 2, 1])
      File ..., line 2, in sort_numbers
        return sorted(numbers)
    NameError: name 'numbers' is not defined

Which gives you a good hint what the problem might be, so you can now fix your
function and try again:

.. code:: python

    >>> #                ↓ typo fixed
    >>> def sort_numbers(numbers):
    ...     return sorted(numbers)
    ...
    >>> with clean_env():
    ...     sort_numbers([0, 2, 1])
    ...
    [0, 1, 2]

By default, ``clean_env`` tries to be "smart" about which globals to remove and
which to keep, e.g. it leaves functions alone, as you've probably noticed, since
we were able to call ``sort_numbers`` within the ``with`` block. If the defaults
don't suit you though, you can tweak its behavior by using blacklists or
whitelists and other options. Check out the documentation for
:func:`corpy.util.clean_env` for further details.

One common case where you might want to change the defaults is to make
``clean_env`` a little bit more lenient, so that it allows all global variables
within the ``with`` block itself, and only starts pruning them inside function
calls. Typically, you'll want to use previously defined (global) variables to
test your functions under ``clean_env``, but by default, you can't, obviously,
because ``clean_env`` hides them:

.. code:: python

    >>> with clean_env():
    ...     sort_numbers(numbers)
    ...
    Traceback (most recent call last):
      File ..., line 2, in <module>
        sort_numbers(numbers)
    NameError: name 'numbers' is not defined

That's where the ``strict=False`` option comes in. In the code below, it allows
referring to the ``numbers`` global variable as part of the ``with`` block, and
only hides it during the function call.

.. code:: python

    >>> with clean_env(strict=False):
    ...     sort_numbers(numbers)
    ...
    [0, 1, 2, 3, 4]

While the non-strict approach is convenient, it requires a slightly different
and more complicated strategy, which makes it somewhat slower. That's why it's
opt-in, even though it's very often what you want.

Breaking code by re-assigning built-in functions
------------------------------------------------

Another type of problem that beginners tend to run into is that they
accidentally overwrite a built-in function. For instance, if you're learning
about sorting, what do you call a list you've just sorted? Well, ``sorted`` of
course!

.. code:: python

    >>> sorted = sorted(numbers)

Unfortunately, now you can't sort anymore -- you've pointed ``sorted`` to your
list, instead of the sorting function it points to by default.

.. code:: python

    >>> sorted(numbers)
    Traceback (most recent call last):
      File ..., line 1, in <module>
        sorted(numbers)
    TypeError: 'list' object is not callable

If this happens in the students' own code, they might realize what they broke
and how to fix it. However, if this ends up breaking example code provided *by
the teacher*, the student might not realize it's their fault -- after all, how
could they break code they didn't write?

This is why by default, ``clean_env`` restores any overwritten builtins, because
it assumes reassigning builtins is a mistake:

.. code:: python

    >>> with clean_env():
    ...     sorted
    ...
    <built-in function sorted>
    >>> sorted
    [0, 1, 2, 3, 4]

.. note::

   If you accidentally overwrite a built-in function, you can get it back by
   importing it from the ``builtins`` module, e.g. ``from builtins import
   sorted``.
