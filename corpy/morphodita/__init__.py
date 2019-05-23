import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__package__)
log.setLevel(logging.INFO)

from .tagger import Tagger  # noqa: E402, F401
