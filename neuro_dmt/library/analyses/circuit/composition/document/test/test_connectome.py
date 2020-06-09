# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 


"""
Test develop documents that analyze circuit connectome.
"""

import os
from pathlib import Path
import pandas as pd
from dmt.tk.journal import Logger
from .. import connectome
from .import get_test_object, get_path_save

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def test_document():
    """
    A documented analysis of layer thickness should:
    1.???
    """
    test_object = get_test_object(connectome, target={"hypercolumn": 2})

    assert test_object.document

    document = test_object.document
    assert document.label == "circuit_connectome"

    report = document(
        test_object.adapter, test_object.circuit_model)
    path_save = get_path_save().joinpath("document")
    path_save.mkdir(parents=False, exist_ok=True)
    document.post(report, path_save, latex=True)

    assert os.path.exists(
        path_save.joinpath("circuit_connectome"))
    assert os.path.exists(
        path_save.joinpath("circuit_connectome", "methods"))
    assert os.path.exists(
        path_save.joinpath("circuit_connectome", "results"))
    assert os.path.isfile(
        path_save.joinpath("circuit_connectome", "report.html"))


    assert os.path.isfile(
        path_save.joinpath("circuit_connectome", "report.tex"))
    path_abstract = path_save.joinpath("circuit_connectome", "abstract")
    assert os.path.isfile(
        path_abstract.joinpath("abstract.tex"))
