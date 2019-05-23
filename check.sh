#!/usr/bin/env bash

flake8
# these are the same settings as enabled by Visual Studio Code, cf:
# https://code.visualstudio.com/docs/python/linting
pylint corpy --unsafe-load-any-extension=y --disable=all --enable=F,E,unreachable,duplicate-key,unnecessary-semicolon,global-variable-not-assigned,unused-variable,binary-op-exception,bad-format-string,anomalous-backslash-in-string,bad-open-mode
pytest
