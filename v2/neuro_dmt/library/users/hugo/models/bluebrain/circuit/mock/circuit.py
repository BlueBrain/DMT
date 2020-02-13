"""
Circuit specific code.
"""
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from .cell import CellCollection
from .connectome import Connectome

from .composition import CircuitComposition
from .builder import CircuitBuilder

logger = Logger(client=__file__)


class MockCircuit(WithFields):
    """
    A class to mock Bluepy circuit.
    We will try to keep this circuit as close to the real one.
    This mock circuit mimics a cortical circuit with 6 layers.
    We assume a simple cuboidal columnar structure, with a square
    as it's base, and layers stacked along the y-axis.
    """
    cells = Field(
        """
        An object representing the cells of this circuit.
        """)
    connectome = Field(
        """
        An object representing the connectome of this circuit.
        """)


    @classmethod
    def build(cls, composition, connectivity):
        """
        Build a circuit with given 'composition', and 'connectivity'.

        Parameters
        composition :: An object parameterizing a circuit's composition.
        connectivity :: An object parameterizing a circuit's connectivity
        """
        circuit_builder =\
            CircuitBuilder(
                composition=composition,
                connectivity=connectivity)
        cell_collection =\
            circuit_builder.get_cell_collection()
        return MockCircuit(
            cells=cell_collection,
            connectome=circuit_builder.get_connectome(cell_collection))
