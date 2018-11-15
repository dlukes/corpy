from setuptools import setup, find_packages

setup(
    name="corpy",
    version="0.0",
    author="David Lukeš",
    author_email="dafydd.lukes@gmail.com",
    description="Tools for processing language data.",
    license="GNU GPLv3",
    url="https://github.com/dlukes/corpy",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "click",
        "lazy",
        "lxml",
        "matplotlib",
        "numpy",
        "regex",
        "ufal.morphodita (>=1.9)",
        "wordcloud",
    ],
    entry_points="""
        [console_scripts]
        xc=corpy.scripts.xc:main
        zip-verticals=corpy.scripts.zip_verticals:main
    """,
)
