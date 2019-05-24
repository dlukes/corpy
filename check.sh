#!/usr/bin/env bash

flake8
pylint corpy
pytest
poetry build
twine check dist/*
