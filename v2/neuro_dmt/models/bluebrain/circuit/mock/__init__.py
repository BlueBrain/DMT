"""
A mock circuit that we can use to test.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from .composition import CircuitComposition
from .builder import CircuitBuilder

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


class MockCircuit(WithFields):
    """
    A class to mock Bluepy circuit.
    We will try to keep this circuit as close to the real one.
    This mock circuit mimics a cortical circuit with 6 layers.
    We assume a simple cuboidal columnar structure, with a square
    as it's base, and layers stacked along the y-axis.
    """
    pass
