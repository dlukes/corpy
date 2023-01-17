"""Top-level CorPy package.

Refer to the documentation of the individual packages for details.

"""
from ._version import __version__, __version_tuple__


def load_ipython_extension(ipython):
    from ._magics import CorpyMagics

    ipython.register_magics(CorpyMagics)
