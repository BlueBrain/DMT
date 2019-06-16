"""
A mock circuit that we can use to test.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields

logger = Logger(client=__file__)

cell_properties =[
    CellProperty.ID,
    CellProperty.LAYER,
    CellProperty.MTYPE,
    CellProperty.MORPHOLOGY,
    CellProperty.MORPH_CLASS,
    CellProperty.ME_COMBO,
    CellProperty.REGION,
    CellProperty.X, CellProperty.Y, CellProperty.Z,
    CellProperty.SYNAPSE_CLASS]


class CircuitComposition(WithFields):
    """
    A data-class to define a circuit's composition.
    We will add fields to this class as we develop MockCircuit.
    """
    layers = Field(
        """
        A tuple containing layer labels.
        We set the default assuming a cortical circuit.
        """,
        __default_value__=(1, 2, 3, 4, 5, 6))
    layer_thickness = Field(
        """
        A dict mapping layer label to its thickness in the column,
        measured in micro-meters.
        """)
    column_base = Field(
        """
        Length of the column's base, measured in micro-meters
        """)
    cell_density = Field(
        """
        A dict mapping layer label to its density of cells,
        measured in number-cells / cubic-mirco-meters.
        """)


class MockCircuit(WithFields):
    """
    A class to mock Bluepy circuit.
    We will try to keep this circuit as close to the real one.
    This mock circuit mimics a cortical circuit with 6 layers.
    We assume a simple cuboidal columnar structure, with a square
    as it's base, and layers stacked along the y-axis.
    """
