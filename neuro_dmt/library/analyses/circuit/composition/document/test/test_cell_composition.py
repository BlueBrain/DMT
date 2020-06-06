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
Test develop documents that analyze circuit composition.
"""

import os
from pathlib import Path
import pandas as pd
from dmt.tk.journal import Logger
from .. import cell_composition
from .import get_test_object, get_path_save

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)


def test_document():
    """
    A documented analysis of cell composition should:
    1.???
    """
    test_object = get_test_object(cell_composition)

    try:
        assert test_object.document
    except AttributeError:
        LOGGER.alert(
            """
            No document in test object:
            \t{}
            """.format(test_object))
        raise AssertionError

    document = test_object.document
    assert document.label == "cell_composition"

    report = document(
        test_object.adapter, test_object.circuit_model)
    path_save = get_path_save().joinpath("document")
    path_save.mkdir(parents=False, exist_ok=True)
    document.post(report, path_save, latex=True)

    assert os.path.exists(
        path_save.joinpath("cell_composition"))
    assert os.path.exists(
        path_save.joinpath("cell_composition", "methods"))
    assert os.path.exists(
        path_save.joinpath("cell_composition", "results"))
    assert os.path.isfile(
        path_save.joinpath("cell_composition", "report.html"))


    assert os.path.isfile(
        path_save.joinpath("cell_composition", "report.tex"))
    path_abstract = path_save.joinpath("cell_composition", "abstract")
    assert os.path.isfile(
        path_abstract.joinpath("abstract.tex"))
