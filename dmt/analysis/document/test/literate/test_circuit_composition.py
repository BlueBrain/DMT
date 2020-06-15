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
Test Develop
Document layer thickness of a circuit.
"""
from ..test_composition import *
from ..import *
from .import get_path_save
from .import circuit_composition

LOGGER = Logger(client=__file__)

LOGGER.status(
    LOGGER.get_source_info(),
    """
    File {}
    """.format(__file__))

def test_document_attributes():
    document = circuit_composition.document

    assert hasattr(document, "cell_density")
    assert hasattr(document.cell_density, "measurement")
    assert callable(document.cell_density.measurement),\
        type(document.cell_density.measurement)
    assert hasattr(document.cell_density, "illustration")
    assert callable(document.cell_density.illustration),\
        type(document.cell_density.illustration)

    assert hasattr(document, "inhibitory_fraction")
    assert hasattr(document.inhibitory_fraction, "measurement")
    assert callable(document.inhibitory_fraction.measurement)
    assert hasattr(document.inhibitory_fraction, "illustration")
    assert callable(document.inhibitory_fraction.illustration)

    report = document.get()
    path_save = get_path_save().joinpath("document")
    path_save.mkdir(parents=False, exist_ok=True)

    adapter = MockAdapter()
    model = MockModel()
    value_report = report(adapter, model)
    path_report = report.save(value_report, path_save)

    assert path_report._ == path_save.joinpath("circuit_composition")
    test_abstract(Record(
        instance=report.abstract,
        value=value_report.abstract,
        path_save=path_report._))
    test_introduction(Record(
        instance=report.introduction,
        value=value_report.introduction,
        path_save=path_report._))
    test_methods(Record(
        instance=report.methods,
        value=value_report.methods,
        path_save=path_report._))
    test_results(Record(
        instance=report.results,
        value=value_report.results,
        path_save=path_report._))
