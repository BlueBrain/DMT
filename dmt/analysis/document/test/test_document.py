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
Test develop document components.
"""
from .test_composition import\
    test_abstract,\
    test_introduction,\
    test_methods,\
    test_results
from .test_composition import *
from .import *


def test_lab_report():
    """
    A basic lab report should have:
    0. Abstract
    1. Introduction
    2. Methods
    3. Results
    """
    adapter = MockAdapter()
    model = MockModel()
    mock_experimental_figures = Bars(
        xvar="layer", xlabel="Layer",
        yvar="cell_density", ylabel="Cell Density"
    )(mock_cell_density())
    mock_experimental_figures.update(Bars(
        xvar="layer", xlabel="Layer",
        yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"
    )(mock_inh_fraction()))

    plotter_cd = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density"))
    plotter_if = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"))

    report = LabReport(
        title="MockAnalysis",
        phenomenon="Composition",
        abstract=get_abstract(),
        introduction=get_introduction(),
        methods=get_methods(),
        results=get_results())

    path_save = get_path_save()
    value_report = report(adapter, model)
    path_report = report.save(value_report, path_save)

    assert path_report == path_save.joinpath("report")
    test_abstract(Record(
        abstract=report.abstract,
        value=value_report.abstract,
        path_save=path_report))
    test_introduction(Record(
        introduction=report.introduction,
        value=value_report.introduction,
        path_save=path_report))
    test_methods(Record(
        methods=report.methods,
        value=value_report.methods,
        path_save=path_report))
    test_results(Record(
        results=report.results,
        value=value_report.results,
        path_save=path_report))
