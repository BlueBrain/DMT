# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop by layer composition analyses.
"""

import numpy
import pandas
from dmt.tk.field import lazyproperty
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from ....circuit import BrainCircuitAnalysis
from ..interfaces import CellDensityAdapterInterface
from neuro_dmt.models.bluebrain.circuit.mock.adapter import MockCircuitAdapter
#from neuro_dmt.data import ratt


cell_density_phenomenon =\
    Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")
cell_density_analysis =\
    BrainCircuitAnalysis(
        phenomenon=cell_density_phenomenon,
        AdapterInterface=CellDensityAdapterInterface,
        measurement_parameters=Parameters(
            pandas.DataFrame({"layer": range(1, 7)})),
        plotter=Bars(
            xvar="layer",
            xlabel="Layer",
            yvar=cell_density_phenomenon.label,
            ylabel=cell_density_phenomenon.name),
        adapter=MockCircuitAdapter())

def get_random_dataset(index):
    return cell_density_analysis\
        ._get_statistical_measurement(None, sample_size=1)\
        .reset_index()\
        .assign(dataset="Dataset_{}".format(index))\
        .set_index(
            ["dataset"] + cell_density_analysis.measurement_parameters.variables)

# random_reference_datasets = pandas.concat([
#     get_random_dataset(index)
#     for index in range(3)])
# reference_datasets = pandas\
#     .concat([
#         rat.defelipe2014\
#            .summary_measurement\
#            .samples(1000)\
#            .assign(dataset="DeFelipe2014"),
#         rat.defelipe2017\
#            .summary_measurement\
#            .samples(1000)\
#            .assign(dataset="DeFelipe2017"),
#         rat.meyer2010\
#            .samples(1000)\
#            .assign(dataset="Meyer2010")])\
#     .reset_index()\
#     .set_index(["dataset", "layer"])


# cell_density_validation =\
#     BrainCircuitAnalysis(
#         phenomenon=cell_density_phenomenon,
#         AdapterInterface=CellDensityAdapterInterface,
#         reference_data=reference_datasets,
#         measurement_parameters=Parameters(
#             pandas.DataFrame({"layer": range(1, 7)})),
#         plotter=Bars(
#             xvar="layer",
#             xlabel="Layer",
#             yvar=cell_density_phenomenon.label,
#             ylabel=cell_density_phenomenon.name,
#             gvar="dataset"),
#         adapter=MockCircuitAdapter())



