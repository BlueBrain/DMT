"""
Test develop by layer composition analyses.
"""

import pandas
from dmt.tk.field import lazyproperty
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from ....circuit import BrainCircuitAnalysis
from ..interfaces import CellDensityAdapterInterface
from neuro_dmt.models.bluebrain.circuit.mock.adapter import MockCircuitAdapter


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

reference_datasets = pandas.concat([
    get_random_dataset(index)
    for index in range(3)])

cell_density_validation =\
    BrainCircuitAnalysis(
        phenomenon=cell_density_phenomenon,
        AdapterInterface=CellDensityAdapterInterface,
        reference_data=reference_datasets,
        measurement_parameters=Parameters(
            pandas.DataFrame({"layer": range(1, 7)})),
        plotter=Bars(
            xvar="layer",
            xlabel="Layer",
            yvar=cell_density_phenomenon.label,
            ylabel=cell_density_phenomenon.name,
            gvar="dataset"),
        adapter=MockCircuitAdapter())

