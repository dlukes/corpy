# TODO: Put positions in a buffer (queue). Yield the middle position and give a handle on the
# context to match and count functions. Gotchas: sattrs will have to be reimplemented if they're to
# be available on the context; corpora shorter than the queue size; start and end corner cases
# (before the queue fills up / as it's emptying out).

import sys
import gzip
import os.path as osp
from typing import List

import re
import datetime as dt
from collections import namedtuple, defaultdict

import numpy as np

__all__ = ["Vertical", "Syn2015Vertical", "ipm", "arf"]

Structure = namedtuple("Structure", "name attrs")
UtklTag = namedtuple(
    "UtklTag", "pos sub gen num case pgen pnum pers tense grad neg act p13 p14 var asp"
)


class Vertical:
    """Base class for a corpus in the vertical format.

    Create subclasses for specific corpora by at least specifying a list of :attr:`struct_names` and
    :attr:`posattrs`.

    """

    struct_names: List[str] = []
    posattrs: List[str] = []

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
        return open(self.path, "rt")

    def parse_position(self, position):
        return self.position_template(*position.split("\t"))

    def positions(self, parse_sattrs=True, ignore_fn=None, hook_fn=None):
        self.sattrs = {}
        # ignore_fn specifies which positions to completely ignore, based on pos and struct attrs
        # hook_fn is a function to be called at each position (receives pos and struct attrs)
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
        # match_fn specifies what to match, based on pos and struct attrs
        # count_fn specifies what to count, based on pos and struct attrs; if it returns a list,
        # it's understood as a list of things to count
        if count_fn is None:
            count_fn = match_fn
        index = defaultdict(list)
        for i, position in enumerate(self.positions(**kwargs)):
            if match_fn(position, self.sattrs):
                count = count_fn(position, self.sattrs)
                if isinstance(count, list):
                    for c in count:
                        index[c].append(i)
                else:
                    index[count].append(i)
        index = {k: np.array(v) for k, v in index.items()}
        return index, i


class Syn2015Vertical(Vertical):
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
    struct_names = ["block"] + Syn2015Vertical.struct_names


def ipm(occurrences, N):
    return 1e6 * len(occurrences) / N


def arf(occurrences, N):
    freq = len(occurrences)
    if freq == 0:
        return 0
    shifted = np.roll(occurrences, 1)
    distances = (occurrences - shifted) % N
    avg_dist = N / freq
    return sum(min(d, avg_dist) for d in distances) / avg_dist
