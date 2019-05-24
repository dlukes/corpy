"""Convenient and easy-to-use MorphoDiTa wrappers.

See the documentation of the individual modules for further details.

"""
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__package__)
LOG.setLevel(logging.INFO)

from .tagger import Tagger  # noqa: E402, F401
from .tokenizer import Tokenizer  # noqa: E402, F401
