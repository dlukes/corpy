from setuptools import setup, find_packages

setup(
    name="corpy",
    version="dev",
    author="David Lukeš",
    author_email="dafydd.lukes@gmail.com",
    description="Tools for processing language data.",
    license="GNU GPLv3",
    url="https://github.com/dlukes/corpy",

    packages=find_packages(),
    install_requires=[
        "click",
        "lazy",
        "lxml",
        "numpy",
        "regex",
        "ufal.morphodita (>=1.9)",
    ],
    entry_points="""
        [console_scripts]
        xc=corpy.scripts.xc:main
    """
)
