# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Circuit composition analyses.
"""
import pandas
from ....circuit import BrainCircuitAnalysis
from ..interfaces import CellDensityAdapterInterface
from dmt.tk.field import lazyproperty
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters

class ByLayerCompositionAnalysis(
        BrainCircuitAnalysis):
    """
    Common attributes of all by layer `CompositionAnalysis` types.
    """
    measurement_parameters = Parameters(
        pandas.DataFrame({"layer": [1, 2, 3, 4, 5, 6]}))

    @lazyproperty
    def plotter(self):
        return Bars(
            xvar="layer",
            xlabel="Layer",
            yvar=self.phenomenon.label,
            ylabel=self.phenomenon.name)


cell_density_phenomenon = Phenomenon(
    "Cell Density",
    "Count of cells in a unit volume.",
    group="composition")

class ByLayerCellDensityAnalysis(
        ByLayerCompositionAnalysis):
    """
    Analysis of cell density by layer.
    The `Field` values assigned below are the simplest applicable values.
    You may customize them.
    """
    phenomenon = cell_density_phenomenon

    AdapterInterface =\
        CellDensityAdapterInterface


cell_density_analysis = BrainCircuitAnalysis(
    phenomenon=cell_density_phenomenon,
    AdapterInterface=CellDensityAdapterInterface,
    measurement_parameters=Parameters(
        pandas.DataFrame({"layer": range(1, 7)})),
    plotter=Bars(
        xvar="layer",
        xlabel="Layer",
        yvar=cell_density_phenomenon.label,
        ylabel=cell_density_phenomenon.name))
