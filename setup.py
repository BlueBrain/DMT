#!/usr/bin/env python
# pylint: disable=F0401,E0611,W0142
import sys
from setuptools import setup

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported.")

setup(
    name="DataModelsAndTests",
    version="0.0.1",
    packages=["dmt", "neuro_dmt"],
    install_requires=[
        "numpy>=1.18.0",
        "pandas>=0.25.1",
        "neurom>=1.3.0",
        "PyYAML>=3.10",
        "bluepysnap>=0.0.0",
        "Cheetah3",
        "nose>=1.3",
        "pytest>=5.1.3"],
    author="Blue Brain Project",
    author_email="",
    description="Analyze and validate computational models",
    license="GPL",
    url="https://github.com/BlueBrain/DMT/issues",
    download_url="https://github.com/BlueBrain/DMT",
    include_package_data=False,
    keywords=(
        'computational neuroscience',
        'computational models',
        'analysis',
        'BlueBrainProject'),
    classifiers=[
        'Development Status :: Alpha',
        'Environment :: Console',
        'License :: GPL',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities'],
    )
