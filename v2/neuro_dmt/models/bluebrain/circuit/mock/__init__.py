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
        __default_value__=np.array((1, 2, 3, 4, 5, 6)))
    layers_ordered = Field(
        """
        Layers ordered by their position.
        """,
        __default_value__=(np.array((6, 5, 4, 3, 2, 1))))
    thickness_layer = Field(
        """
        A dict mapping layer label to its thickness in the column,
        measured in micro-meters.
        """)
    base_column = Field(
        """
        Length of the column's base, measured in micro-meters
        """)
    mtypes = Field(
        """
        A list of mtypes in the circuit.
        """)
    cell_density = Field(
        """
        A dict mapping layer label to its density of cells,
        measured in number-cells / cubic-mirco-meters.
        """)

    def x_range(self, layer=None, mtype=None):
        """
        A two-tuple of floats giving the range of X axis: (xmin, xmax)
        """
        return (0., self.base_column)

    def y_range(self, layer, mtype=None):
        """
        A two-tuple of floats giving the range of Y axis: (ymin, ymax)
        """
        thicknesses =\
            np.array([
                self.thickness_layer[layer]
                for layer in self.layers_ordered])
        position_start_layer =\
            np.array([
                np.sum(thicknesses[0:i])
                for i in range(len(thicknesses))])
        position_end_layer =\
            position_start_layer + thicknesses
        index_layer ={
            layer: index
            for index, layer in enumerate(self.layers_ordered)}
        return (
            position_start_layer[index_layer[layer]],
            position_end_layer[index_layer[layer]])

    def z_range(self, layer=None, mtype=None):
        """
        A two-tuple of floats giving the range of Z axis: (zmin, zmax)
        """
        return (0., self.base_column)


class MockCircuit(WithFields):
    """
    A class to mock Bluepy circuit.
    We will try to keep this circuit as close to the real one.
    This mock circuit mimics a cortical circuit with 6 layers.
    We assume a simple cuboidal columnar structure, with a square
    as it's base, and layers stacked along the y-axis.
    """
