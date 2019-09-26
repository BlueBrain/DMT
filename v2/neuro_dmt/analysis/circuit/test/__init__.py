"""
Test, and develop `BrainCircuitAnalysis`
"""
import pytest as pyt
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting.bars import Bars
from dmt.tk.parameters import Parameters
from dmt.tk.reporting import Report, Reporter
from ..composition.interfaces import CellDensityAdapterInterface
from .. import BrainCircuitAnalysis
from neuro_dmt.models.bluebrain.circuit.test import mock

def test_adapter_resolution():
    """
    `BrainCircuitAnalysis` should be able to resolve which adapter to use.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    model = mock.get_circuit_model()
    adapter = mock.get_circuit_adapter(model)
    analysis =\
        BrainCircuitAnalysis(
            phenomenon=cell_density_phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=cell_density_phenomenon.label,
                ylabel=cell_density_phenomenon.name,
                gvar="dataset"))

    with pyt.raises(AttributeError):
        analysis(model)

    with pyt.raises(TypeError):
        analysis._resolve_adapter_and_model(model)

    analysis.adapter = adapter

    assert analysis._resolve_adapter_and_model(model) == (adapter, model)

    for a, m in 10 * [(adapter, model)]:
        assert analysis._resolve_adapter_and_model(model) == (a, m)
