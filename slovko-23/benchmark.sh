#!/bin/sh

set -e

Python-3.10.10/python -m venv py3.10-venv
Python-3.11.2/python -m venv py3.11-venv
Python-3.12.0a6/python -m venv py3.12-venv

py3.10-venv/bin/python -m pip install --no-dependencies .. regex
py3.11-venv/bin/python -m pip install --no-dependencies .. regex
py3.12-venv/bin/python -m pip install --no-dependencies .. regex

hyperfine --warmup 1 --shell none \
  'py3.10-venv/bin/python test.py' \
  'py3.11-venv/bin/python test.py' \
  'py3.12-venv/bin/python test.py'
