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

make upgrade_docs
make docs

make clean
make dist

>&2 echo "\
Possible next steps:

- 'make publish' to upload a new release to PyPI
- 'make linkcheck' to check external links"
