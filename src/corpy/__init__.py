"""Top-level CorPy package.

Refer to the documentation of the individual packages for details.

"""
__version__ = "0.3.1"


def load_ipython_extension(ipython):
    from ._magics import CorpyMagics

    ipython.register_magics(CorpyMagics)
