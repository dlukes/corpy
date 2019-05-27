#!/usr/bin/env bash

flake8
pylint corpy
pytest -n auto
# -n is nit-picky mode, which checks for missing references; however, we're only
# interested in missing references to stuff defined as part of corpy
sphinx-build -j auto -Ean docs docs/_build 2>&1 |
  rg "WARNING.*corpy"
# possibly also check external links every now and then
# sphinx-build -b linkcheck docs docs/_build
rm -rf dist
poetry build
twine check dist/*
