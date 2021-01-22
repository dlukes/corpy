"""This is just a dummy file for ReadTheDocs, which installs corpy without any
dependencies, because installing dependencies might fail due to timeouts, memory
limits etc. Installing corpy is needed in order for Sphinx's autodoc features to
work, but the dependencies can be mocked by Sphinx (cf. docs/conf.py).

"""
from setuptools import setup, find_packages

setup(
    name="corpy",
    packages=find_packages(),
    include_package_data=True,
    # just the packages required to *build* the docs (either because they do the
    # building, or because they can't be properly mocked by the builder); most
    # of the actual dependencies are mocked via autodoc_mock_imports
    install_requires=["regex", "sphinx>=3.0,<=4.0", "sphinx-rtd-theme"],
)
