import os.path as osp
import click as cli
import logging as log

import unicodedata as ud
from collections import Counter

import regex as re
from lxml import etree

NAME = osp.splitext(osp.basename(__file__))[0]
LOG = log.getLogger(NAME)
LOGLEVELS = [
    s
    for f, s in sorted(
        (v, k) for k, v in vars(log).items() if k.isupper() and isinstance(v, int)
    )
]
NORM_FORMS = ("NFC", "NFD", "NFKC", "NFKD")


def count_extended_grapheme_clusters(text):
    return Counter(m.group() for m in re.finditer(r"\X", text))


def check_normalization(fdist, expected_form="NFC"):
    LOG.info("Checking normalization of identified extended grapheme clusters.")
    for extended_grapheme_cluster in fdist.keys():
        normalized = ud.normalize(expected_form, extended_grapheme_cluster)
        if extended_grapheme_cluster != normalized:
            LOG.warning(
                f"Expected {normalized!r} according to {expected_form}, got "
                f"{extended_grapheme_cluster!r} instead!"
            )


def parse(file, xml=False):
    if xml:
        LOG.info(f"Parsing {file.name!r} as XML.")
        tree = etree.parse(file)
        for elem in tree.iter():
            yield from elem.attrib.values()
            yield elem.text
            yield elem.tail
    else:
        yield from file


def print_fdist(fdist):
    for extended_grapheme_cluster, count in fdist.most_common():
        names, codepoints = [], []
        for codepoint in extended_grapheme_cluster:
            name = ud.name(codepoint, None)
            # control characters have no names, and for them, we want to print their repr instead
            codepoints.append(repr(codepoint) if name is None else codepoint)
            names.append("__NO_NAME__" if name is None else name)
        print(count, "".join(codepoints), "+".join(names), sep="\t")


@cli.command()
@cli.option(
    "--expected-normalization",
    help="Warn if identified extended grapheme clusters do not "
    "match expected normalization form.",
    type=cli.Choice(NORM_FORMS),
)
@cli.option("--lower", help="Convert to lowercase before processing.", is_flag=True)
@cli.option(
    "--xml",
    help="Parse input as XML and process only text nodes and attribute values.",
    is_flag=True,
)
@cli.option(
    "lvl",
    "--log",
    help="Set logging level.",
    type=cli.Choice(LOGLEVELS),
    default="WARN",
)
@cli.option("--verbose", "-v", help="(Repeatedly) increase logging level.", count=True)
@cli.option("--quiet", "-q", help="(Repeatedly) decrease logging level.", count=True)
@cli.argument("files", type=cli.File("rt", encoding="utf-8"), nargs=-1)
def main(expected_normalization, lower, xml, lvl, verbose, quiet, files):
    """`wc -c` on steroids.

    Count extended grapheme clusters, print their frequency distribution.

    FILES are the files to process. Leave empty or - for STDIN.

    """
    lvl = getattr(log, lvl) - 10 * verbose + 10 * quiet
    log.basicConfig(
        level=lvl, format="[%(asctime)s {}:%(levelname)s] %(message)s".format(NAME)
    )
    files = files if files else (cli.File("rt", encoding="utf-8")("-"),)
    fdist = Counter()
    LOG.info("Aggregating counts of extended grapheme clusters in input.")
    for file in files:
        for fragment in parse(file, xml):
            if fragment is not None:
                fragment = fragment.lower() if lower else fragment
                fdist.update(count_extended_grapheme_clusters(fragment))
    if expected_normalization:
        check_normalization(fdist, expected_normalization)
    print_fdist(fdist)
