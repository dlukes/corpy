"""Parse and query corpora in the vertical format.

"""
# TODO: Put positions in a buffer (queue). Yield the middle position and give a handle on the
# context to match and count functions. Gotchas: sattrs will have to be reimplemented if they're to
# be available on the context; corpora shorter than the queue size; start and end corner cases
# (before the queue fills up / as it's emptying out).

import sys
import gzip
import os.path as osp
from typing import List, NamedTuple

import re
import datetime as dt
from collections import namedtuple, defaultdict

import numpy as np

__all__ = ["Vertical", "Syn2015Vertical", "ipm", "arf"]


class UtklTag(NamedTuple):
    pos: str
    sub: str
    gen: str
    num: str
    case: str
    pgen: str
    pnum: str
    pers: str
    tense: str
    grad: str
    neg: str
    act: str
    p13: str
    p14: str
    var: str
    asp: str


class Vertical:
    """Base class for a corpus in the vertical format.

    Create subclasses for specific corpora by at least specifying a list of
    :attr:`struct_names` and :attr:`posattrs` as class attributes.

    :param path: Path to the vertical file to work with.
    :type path: str

    """

    struct_names: List[str] = []
    """A list of expected structural attribute tag names."""
    posattrs: List[str] = []
    """A list of expected positional attributes."""

    def __init__(self, path):
        if not (self.struct_names and self.posattrs):
            raise Exception(
                f"The class attributes `struct_names` and `posattrs` must be specified. You "
                f"probably want to subclass {self.__class__.__name__!r}."
            )
        if not osp.isfile(path):
            raise Exception(f"File {path!r} does not exist!")
        self.path = path
        self._struct_re = re.compile(
            r"<\s*?(/?)\s*?({})(?:\s*?(/?)\s*?| (.*?))>".format(
                "|".join(self.struct_names)
            )
        )
        self.position_template = namedtuple("Position", self.posattrs)
        # if an integer > 0, then modulo for reporting progress; if falsey, then turns off reporting
        self.report = None

    def open(self):
        """Open the vertical file in :attr:`self.path`.

        Override this method in subclasses to specify alternative ways of
        opening, e.g. using :func:`gzip.open`.

        """
        return open(self.path, "rt")

    def parse_position(self, position):
        """Parse a single position from the vertical.

        Override this method in subclasses to hook into the position parsing
        process.

        """
        return self.position_template(*position.split("\t"))

    def positions(self, parse_sattrs=True, ignore_fn=None, hook_fn=None):
        """Iterate over the positions in the vertical.

        At any point during the iteration, the structural attributes
        corresponding to the current position are accessible via
        :attr:`self.sattrs`.

        :param parse_sattrs: Whether to parse structural attrs into a dict
            (default) or just leave the original string (faster).
        :type parse_sattrs: bool
        :param ignore_fn: If given, then evaluated at each position; if it
            returns ``True``, then the position is completely ignored.
        :type ignore_fn: function(posattrs, sattrs)
        :param hook_fn: If given, then evaluated at each position.
        :type hook_fn: function(posattrs, sattrs)

        """
        self.sattrs = {}
        start = dt.datetime.now()
        with self.open() as file:
            for i, line in enumerate(file):
                line = line.strip(" \n\r")
                m = self._struct_re.fullmatch(line)
                if m:
                    close, tag, self_close, attrs = m.groups()
                    if close:
                        self.sattrs.pop(tag)
                    elif self_close:
                        pass
                    else:
                        # TODO: figure out a way to allow nested tags...?
                        if tag in self.sattrs:
                            raise Exception(
                                f"{tag!r} already in `sattrs`; nested tags?"
                            )
                        if parse_sattrs:
                            attrs = {
                                m.group(1): m.group(2)
                                for m in re.finditer(
                                    r'\s*?(\S+?)="([^"]*?)"',
                                    "" if attrs is None else attrs,
                                )
                            }
                        self.sattrs[tag] = attrs
                else:
                    position = self.parse_position(line)
                    if hook_fn:
                        hook_fn(position, self.sattrs)
                    if not (ignore_fn and ignore_fn(position, self.sattrs)):
                        yield position

                if self.report and i % self.report == 0:
                    time = dt.datetime.now() - start
                    print(f"Processed {i:,} lines in {time}.", file=sys.stderr)

    def search(self, match_fn, count_fn=None, **kwargs):
        """Search the vertical, creating an index of what's been found.

        :param match_fn: Evaluated at each position to see if the position
            matches the given search.
        :type match_fn: function(match_fn, count_fn)
        :param count_fn: Evaluated at each **matching** position to determine
            what should be counted at that position (in the sense of being
            tallied as part of the resulting frequency distribution). If it
            returns a list, it's understood as a list of things to count.
        :param kwargs: Passed on to :meth:`~Vertical.positions`.
        :return: The frequency index of counted "things" and the size of the
            corpus.
        :rtype: (dict, int)

        """
        if count_fn is None:
            count_fn = match_fn
        index = defaultdict(list)
        i = None  # if loop below happens to have 0 iterations, i would be undefined...
        for i, position in enumerate(self.positions(**kwargs)):
            if match_fn(position, self.sattrs):
                count = count_fn(position, self.sattrs)
                if isinstance(count, list):
                    for countable in count:
                        index[countable].append(i)
                else:
                    index[count].append(i)
        index = {k: np.array(v) for k, v in index.items()}
        return index, i if i is None else i + 1  # ... and we need to return it here


class Syn2015Vertical(Vertical):
    """A subclass of :class:`Vertical` for the SYN2015 corpus.

    Refer to :class:`Vertical` for API details.

    """

    struct_names = ["doc", "text", "p", "s", "hi", "lb"]
    posattrs = [
        "word",
        "lemma",
        "tag",
        "proc",
        "afun",
        "parent",
        "eparent",
        "prep",
        "p_lemma",
        "p_tag",
        "p_afun",
        "ep_lemma",
        "ep_tag",
        "ep_afun",
    ]

    def open(self):
        return gzip.open(self.path, "rt")

    def parse_position(self, position):
        position = position.split("\t")
        position[2] = UtklTag(*position[2])
        return self.position_template(*position)


class ShuffledSyn2015Vertical(Syn2015Vertical):
    """A subclass of :class:`Vertical` for the SYN2015 corpus, shuffled.

    Refer to :class:`Vertical` for API details.

    """

    struct_names = ["block"] + Syn2015Vertical.struct_names


def ipm(occurrences, N):
    """Relative frequency of `occurrences` in corpus, in instances per million."""
    return 1e6 * len(occurrences) / N


def arf(occurrences, N):
    """Average reduced frequency of `occurrences` in corpus."""
    freq = len(occurrences)
    if freq == 0:
        return 0
    shifted = np.roll(occurrences, 1)
    distances = (occurrences - shifted) % N
    avg_dist = N / freq
    return sum(min(d, avg_dist) for d in distances) / avg_dist
