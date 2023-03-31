#!/bin/sh

set -e

Python-3.10.10/python -m venv py3.10-venv
Python-3.11.2/python -m venv py3.11-venv

py3.10-venv/bin/python -m pip install --no-dependencies .. regex ufal.morphodita numpy
py3.11-venv/bin/python -m pip install --no-dependencies .. regex ufal.morphodita numpy

hyperfine --warmup 1 --shell none \
  'py3.10-venv/bin/python test.py' \
  'py3.11-venv/bin/python test.py'
