#!/bin/sh

cd "$(dirname "$(realpath "$0")")"
source $(poetry env info -p)/bin/activate ||
  { >&2 echo 'Failed to activate project virtualenv!' && exit 1; }
set -e

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

flake8 corpy
pylint corpy
pytest -n auto
>&2 echo "Building docs; if it hangs, re-run without '-j auto' and redirection to get helpful error output."
# -n is nit-picky mode, which checks for missing references; however, we're only
# interested in missing references to stuff defined as part of corpy, and not
# the warning emitted upon importing corpy when no IPython session is found
sphinx-build -j auto -Ean docs docs/_build 2>&1 |
  { grep -P "WARNING.*corpy" || [ $? == 1 ]; } |
  { grep -Pv "IPython session not found" || [ $? == 1 ]; }
# possibly also check external links every now and then
# sphinx-build -b linkcheck docs docs/_build
rm -rf dist
poetry build
twine check dist/*
