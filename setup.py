from setuptools import setup, find_packages


def build_native(spec):
    # Step 1: build the rust library
    build = spec.add_external_build(
        cmd=["cargo", "build"],
        # cmd=["cargo", "build", "--release"],
        path="./rust"
    )

    # Step 2: add a cffi module based on the dylib we built
    #
    # We use lambdas here for dylib and header_filename so that those are
    # only called after the external build finished.
    spec.add_cffi_module(
        module_path="corpy._native",
        dylib=lambda: build.find_dylib("corpy", in_path="target/debug"),
        # dylib=lambda: build.find_dylib("corpy", in_path="target/release"),
        header_filename=lambda: build.find_header("corpy.h", in_path="target"),
        rtld_flags=["NOW", "NODELETE"]
    )


setup(
    name="corpy",
    version="0.1",
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
        "milksnake",
        "numpy",
        "regex",
        "ufal.morphodita (>=1.9)",
    ],
    entry_points="""
        [console_scripts]
        xc=corpy.scripts.xc:main
        zip-verticals=corpy.scripts.zip_verticals:main
    """,
    # rust native extension setup via milksnake
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    milksnake_tasks=[
        build_native,
    ]
)
