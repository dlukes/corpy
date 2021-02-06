import os.path as osp
import click as cli
import logging as log

NAME = osp.splitext(osp.basename(__file__))[0]
LOG = log.getLogger(NAME)
LOGLEVELS = [
    s
    for f, s in sorted(
        (v, k) for k, v in vars(log).items() if k.isupper() and isinstance(v, int)
    )
]


def print_position(lines, line_no):
    lines = [line.strip(" \n").split("\t") for line in lines]
    word = lines[0][0]
    position = [word]
    for i, line in enumerate(lines):
        assert line[0] == word, (
            f"Expected first attribute {word} but got {line[0]} in vertical "
            f"#{i+1} at line #{line_no+1}. Are you sure the verticals "
            "represent the same corpus?"
        )
        position.extend(line[1:])
    print("\t".join(position))


@cli.command()
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
def main(lvl, verbose, quiet, files):
    """Zip verticals together.

    Intended for "zipping" together verticals of the same corpus. At least one of them must have
    multiple positional attributes. Structures and the first positional attribute (which is included
    only once) are taken from the first vertical provided.

    FILES are the files to process. Leave empty or - for STDIN.

    """
    lvl = getattr(log, lvl) - 10 * verbose + 10 * quiet
    log.basicConfig(
        level=lvl, format="[%(asctime)s {}:%(levelname)s] %(message)s".format(NAME)
    )
    files = files if files else (cli.File("rt", encoding="utf-8")("-"),)
    LOG.info(f"Zipping the following vertical files: {files}")
    for line_no, lines in enumerate(zip(*files)):
        if any("\t" in line for line in lines):
            print_position(lines, line_no)
        else:
            print(lines[0].strip(" \n"))
    LOG.info("Done.")
