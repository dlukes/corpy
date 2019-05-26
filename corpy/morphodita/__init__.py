"""Convenient and easy-to-use MorphoDiTa wrappers.

"""
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__package__)
LOG.setLevel(logging.INFO)

from .tokenizer import Tokenizer  # noqa: E402, F401
from .tagger import Tagger  # noqa: E402, F401
