"""
A mock circuit that we can use to test.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid

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
    length_base = Field(
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

    @property
    def height(self):
        """
        Total height of the column, that can be described in terms of the
        layer thicknesses.
        """
        return np.sum([
            thickness for thickness in self.thickness_layer.values()])

    @property
    def number_layers(self):
        """
        number of layers
        """
        return len(self.layers)

    @property
    def thicknesses(self):
        """
        An array of layer thickness ordered as 'layers_ordered'.
        """
        return np.array([
            self.thickness_layer[layer]
            for layer in self.layers_ordered])

    @property
    def order_index_layer(self):
        """
        A dict mapping layer to its (positional) order.
        """
        return {
            layer: index
            for index, layer in enumerate(self.layers_ordered)}

    def x_range(self, layer=None, mtype=None):
        """
        A two-tuple of floats giving the range of X axis: (xmin, xmax)
        """
        return (0., self.length_base)

    def y_range(self, layer, mtype=None):
        """
        A two-tuple of floats giving the range of Y axis: (ymin, ymax)
        """
        position_start_layer =\
            np.array([
                np.sum(self.thicknesses[0:i])
                for i in range(self.number_layers)])
        position_end_layer =\
            position_start_layer + self.thicknesses
        return (
            position_start_layer[self.order_index_layer[layer]],
            position_end_layer[self.order_index_layer[layer]])

    def z_range(self, layer=None, mtype=None):
        """
        A two-tuple of floats giving the range of Z axis: (zmin, zmax)
        """
        return (0., self.length_base)

    @property
    def column(self):
        """
        The geometric column
        """
        return Cuboid(
            np.array([0., 0., 0.]),
            np.array([self.length_base, self.height, self.length_base]))

    def bounding_box(self, layer=None, *args):
        """
        The box bounding 'layer'.

        """
        y_range =\
            self.y_range(layer, *args)
        return (
            np.array([0., y_range[0], 0.]),
            np.array([self.length_base, y_range[1], self.length_base]))


class MockCircuit(WithFields):
    """
    A class to mock Bluepy circuit.
    We will try to keep this circuit as close to the real one.
    This mock circuit mimics a cortical circuit with 6 layers.
    We assume a simple cuboidal columnar structure, with a square
    as it's base, and layers stacked along the y-axis.
    """
    pass
