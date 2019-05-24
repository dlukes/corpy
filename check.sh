#!/usr/bin/env bash

flake8
pylint corpy
pytest -n auto
poetry build
twine check dist/*
