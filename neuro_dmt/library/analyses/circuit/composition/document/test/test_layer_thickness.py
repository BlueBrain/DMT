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
from .. import layer_thickness
from .import get_test_object, get_path_save

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def test_document_methods():
    """..."""
    test_object = get_test_object(layer_thickness)

    adapter = test_object.adapter
    circuit_model = test_object.circuit_model

    methods = test_object.document.methods

    assert "cortical_thickness" in methods.measurements
    cortical_thickness =\
        methods.measurements["cortical_thickness"]
    value_cortical_thickness =\
        cortical_thickness(adapter, circuit_model)
    assert isinstance(value_cortical_thickness, pd.DataFrame)
    assert "cortical_thickness" in value_cortical_thickness
    assert "region" in value_cortical_thickness.index.names
    assert "layer" not in value_cortical_thickness.index.names

    assert "relative_thickness" in test_object.document.methods.measurements
    relative_thickness =\
        test_object.document.methods.measurements["relative_thickness"]
    value_relative_thickness =\
        relative_thickness(adapter, circuit_model)
    assert isinstance(value_relative_thickness, pd.DataFrame),\
        type(value_relative_thickness)
    assert "relative_thickness" in value_relative_thickness
    assert "region" in value_relative_thickness.index.names
    assert "layer" in value_relative_thickness.index.names

    value_methods = methods(adapter, circuit_model)
    path_save = get_path_save().joinpath("layer_thickness")
    path_save.mkdir(parents=False, exist_ok=True)
    methods.save(value_methods, path_save)
    path_methods = path_save.joinpath("methods")
    assert os.path.exists(path_methods)
    assert os.path.isfile(path_methods.joinpath("narrative.txt"))
    assert os.path.isfile(path_methods.joinpath("measurements.json"))

    return True

def test_document_results():
    """..."""
    test_object = get_test_object(layer_thickness)

    adapter = test_object.adapter
    circuit_model = test_object.circuit_model

    results = test_object.document.results

    value_results = results(adapter, circuit_model)
    path_save = get_path_save().joinpath("layer_thickness")
    path_save.mkdir(parents=False, exist_ok=True)
    results.save(value_results, path_save)
    path_results = path_save.joinpath("results")

    assert os.path.exists(path_results)
    assert os.path.isfile(path_results.joinpath("narrative.txt"))

    path_measurements = path_results.joinpath("measurements")
    assert os.path.exists(path_measurements)
    assert os.path.isfile(
        path_measurements.joinpath("cortical_thickness.csv"))
    assert os.path.isfile(
        path_measurements.joinpath("relative_thickness.csv"))

    path_illustration = path_results.joinpath("illustration")
    assert os.path.exists(path_illustration)
    path_cortical_thickness =\
        path_illustration.joinpath("cortical_thickness")
    assert os.path.exists(path_cortical_thickness)
    assert os.path.isfile(path_cortical_thickness.joinpath("caption.txt"))
    path_relative_thickness =\
        path_illustration.joinpath("relative_thickness")
    assert os.path.exists(path_relative_thickness)
    assert os.path.isfile(path_relative_thickness.joinpath("caption.txt"))

    return True

def test_document():
    """
    A documented analysis of layer thickness should:
    1.???
    """
    test_object = get_test_object(layer_thickness)

    assert test_object.document

    document = test_object.document
    assert document.label == "layer_thickness"

    report = document(
        test_object.adapter, test_object.circuit_model)
    path_save = get_path_save().joinpath("document")
    path_save.mkdir(parents=False, exist_ok=True)
    document.post(report, path_save, latex=True)

    assert os.path.exists(
        path_save.joinpath("layer_thickness"))
    assert os.path.exists(
        path_save.joinpath("layer_thickness", "methods"))
    assert os.path.exists(
        path_save.joinpath("layer_thickness", "results"))
    assert os.path.isfile(
        path_save.joinpath("layer_thickness", "report.html"))


    assert os.path.isfile(
        path_save.joinpath("layer_thickness", "report.tex"))
    path_abstract = path_save.joinpath("layer_thickness", "abstract")
    assert os.path.isfile(
        path_abstract.joinpath("abstract.tex"))
