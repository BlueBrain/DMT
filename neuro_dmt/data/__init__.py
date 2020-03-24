"""
Datasets created / used at the BlueBrain project.
"""
import os
import sys

LOCATION = os.path.join(
    os.environ.get(
        "DMTPATH",
        os.path.join(
            "/gpfs/bbp.cscs.ch/home",
            "sood/work/validations/dmt")),
    "examples/datasets")
