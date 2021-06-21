#!/bin/sh

cd "$(dirname "$(realpath "$0")")"
# Make sure package and dependencies are up-to-date inside the project
# virtualenv. This is needed for steps that run on the installed package, not
# the source tree:
#
# - testing (tests should pass with the latest compatible dependencies)
# - exporting ReadTheDocs requirements
# - building the docs
poetry install
poetry update
. $(poetry env info -p)/bin/activate ||
  { >&2 echo 'Failed to activate project virtualenv!' && exit 1; }

udpipe_model=czech-pdt-ud-2.4-190531.udpipe
if [ ! -f "$udpipe_model" ]; then
  >&2 echo "Fetching $udpipe_model..."
  curl --silent --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/"$udpipe_model"
fi

morphodita=czech-morfflex-pdt-161115
morphodita_zip="$morphodita".zip
morphodita_tagger="$morphodita".tagger
if [ ! -f "$morphodita_tagger" ]; then
  >&2 echo "Fetching $morphodita_zip..."
  curl --silent --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1836/"$morphodita_zip"
  >&2 echo "Extracting $morphodita_tagger..."
  unzip -q "$morphodita_zip"
  mv "$morphodita/$morphodita_tagger" .
  rm -rf "$morphodita" "$morphodita_zip"
fi

flake8 src/corpy
pylint src/corpy
pytest -n auto

# update ReadTheDocs requirements
rtd_reqs=docs/requirements.txt
echo "# ---8<--- MANAGED BY check.sh; DO NOT EDIT! --->8---" >"$rtd_reqs"
poetry export --dev --without-hashes |
  grep -P '^(sphinx|furo|ipython)==' >>"$rtd_reqs"
echo "# ---8<----------------------------------------->8---" >>"$rtd_reqs"

>&2 echo "Building docs; if it hangs, re-run without '-j auto' and redirection to get helpful error output."
# -n is nit-picky mode, which checks for missing references; however, we're only
# interested in missing references to stuff defined as part of corpy, and not
# the warning emitted upon importing corpy when no IPython session is found
sphinx-build -j auto -Ean docs docs/_build 2>&1 |
  { grep -P "WARNING.*corpy" || [ $? = 1 ]; } |
  { grep -Pv "IPython session not found" || [ $? = 1 ]; }
# possibly also check external links every now and then
# sphinx-build -b linkcheck docs docs/_build

rm -rf dist
poetry build
twine check dist/*
