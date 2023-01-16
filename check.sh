#!/bin/bash

set -eufo pipefail
cd "$(dirname "$(realpath "$0")")"

# Make sure package and dependencies are up-to-date. This is needed for steps
# that run on the installed package, not the source tree:
#
# - testing (tests should pass with the latest compatible dependencies)
# - exporting ReadTheDocs requirements
# - building the docs
make upgrade
make models
make test

# update ReadTheDocs requirements
rtd_reqs=docs/requirements.txt
echo "# ---8<--- MANAGED BY check.sh; DO NOT EDIT! --->8---" >"$rtd_reqs"
venv/bin/python -m pip freeze |
  grep -iP '^(sphinx|furo|ipython)==' >>"$rtd_reqs"
echo "# ---8<----------------------------------------->8---" >>"$rtd_reqs"

>&2 echo "Building docs; if it hangs, re-run without '-j auto' and redirection to get helpful error output."
# -n is nit-picky mode, which checks for missing references; however, we're only
# interested in missing references to stuff defined as part of corpy, and not
# the warning emitted upon importing corpy when no IPython session is found
venv/bin/sphinx-build -j auto -Ean docs docs/_build 2>&1 |
  { grep -P "WARNING.*corpy" || [ $? = 1 ]; } |
  { grep -Pv "IPython session not found" || [ $? = 1 ]; }
# possibly also check external links every now and then
# venv/bin/sphinx-build -b linkcheck docs docs/_build

make clean
make dist
>&2 echo "Run make publish to upload a new release to PyPI."
