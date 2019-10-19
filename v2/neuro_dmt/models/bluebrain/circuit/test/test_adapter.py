"""
Test adapter for Blue Brain circuit models.
"""

import numpy
import pandas
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.collections import take
from neuro_dmt.models.bluebrain.circuit.model import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainCircuitAdapter
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces\
    import CellDensityAdapterInterface
from neuro_dmt.terminology import measurement_method
from .import get_path_circuit

cell_density_phenomenon =\
    Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")

adapter = BlueBrainCircuitAdapter()

def test_cell_density():
    """
    Adapter should be able get cell densities from the model.
    """
    circuit_model = BlueBrainCircuitModel(
        path_circuit_data=get_path_circuit("S1RatSSCxDisseminationBio2"))
    layers = range(1, 7)
    sample_size = 20

    cell_density_samples = pandas\
        .DataFrame(dict(
            layer =[
                layer
                for layer in layers for _ in range(sample_size)],
            cell_density =[
                adapter.get_cell_density(circuit_model, layer=layer)
                for layer in layers for _ in range(sample_size)]))\
        .set_index("layer")

    cell_density_overall = pandas\
        .DataFrame(dict(
            layer =[
                layer
                for layer in layers],
            cell_density =[
                adapter.get_cell_density(
                    circuit_model,
                    layer=layer,
                    method=measurement_method.exhaustive)
                for layer in layers]))\
        .set_index("layer")

    return cell_density_samples, cell_density_overall