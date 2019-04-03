
import os
from setuptools import setup, find_packages

__dir__ = os.path.dirname(__file__)

with open(
    os.path.join(__dir__, "fc_cycle", "__init__.py")
) as f:
    __version__ = "0.0.0"

    for line in f:
        if "#" in line:
            line = line[:line.index("#")]

        if not line.startswith("__version__ ="):
            continue

        __version__ = line.split("=")[1].strip().strip("\"")


setup(
    name="FC-Cycle",
    version=__version__,
    description=(
        "Cycler program for Gilson FC 204 Fraction Collector."
    ),
    url="https://github.com/white-lab/fc-cycle",
    author="Nader Morshed",
    author_email="morshed@mit.edu",
    license="BSD",
    packages=find_packages(exclude=["*.tests", "tests"]),
    install_requires=[
        "pyserial==3.3",
    ],
    dependency_links=[],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
    ],
    test_suite="tests",
)
