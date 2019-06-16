"""
Definitions and methods for cells of a MockCircuit.
"""

from bluepy.v2.enums import Cell as CellProperty

from dmt.tk.field import Field, Property, WithFields
from . import CircuitComposition

MTYPE = CellProperty.MTYPE
REGION = CellProperty.REGION
LAYER = CellProperty.LAYER

class Cell(WithFields):
    """
    Defines a cell, and documents it's (data) fields.
    This class is mostly for documenting and learning purposes.
    """
    region = Field(
        """
        Label of the region where this cell lies.
        For example, 'SSCx', 'Somatosensory-cortex'.
        """,
        __default_value__="brain")
    layer = Field(
        """
        Label of the layer that this cell lies in.
        Field 'layer' makes sense for brain areas with layers,
        such as the cortex, and the hippocampus.
        """,
        __required__=None)
    nucleus = Field(
        """
        Nucleus of cells among which this cell lies.
        Field 'nucleus' makes sense for brain areas like the thalamus.
        (Check facts, I am making things up.)
        """,
        __required__=None)
    mtype = Field(
        """
        The morphological type of this cell.
        The mtype must be one of several categories.
        """)
    etype = Field(
        """
        The electrical type this cell.
        The etype must be one of several categories.
        """)
    morph_class = Field(
        """
        The morphological class of this cell's morphology
        (categorized as mtype). There are at least two morphological classes,
        namely 'PYR' (pyramidal cells) and 'INT' (interneuron cells).
        """)
    synapse_class = Field(
        """
        Synapse class of a cell is either EXCitatory or INHibitory.
        """)



class CircuitBuilder(WithFields):
    """
    Builds a circuit.
    """

    composition = Field(
        """
        Composition of the circuit.
        """,
        __type__=CircuitComposition)

    @property
    def get_cell_density(self,
            region=None,
            layer=None,
            mtype=None):
        """
        Density of cells of given 'mtype' in given 'region' and 'layer'.
        At least one of 'region', 'layer', 'mtype' must be specified.
        """
        assert region or layer or mtype,\
            "region, layer, mtype all invalid."
        if not mtype:
            return\
                self.composition\
                    .cell_density.xs(
                        (region, layer) if region else (layer),
                        label=(REGION, LAYER) if region else (LAYER))

    def get_cell_density(self, mtype, layer, region=None):
        """
        Density of cells of given 'mtype' in given 'layer'.
        """
        return\
            self.composition\
                .cell_density.xs(
                    (mtype, region, layer) if region else (mtype, layer),
                    level=(MTYPE, REGION, LAYER) if region else (MTYPE, LAYER))

    def get_number_cells(self, layer, mtype, region=None):
        """
        How many cells of given 'mtype' in a given 'layer'?
        """
        volume =\
            self.composition.thickness_layer[layer] *\
            self.composition.base_column ** 2
        return int(
            self.get_cell_density(region, layer, mtype) * volume)


    def place_cells(self):
        """
        Place cells.
        1. Generate cells for each layer
        2. Place them.

        Arguments
        ------------
        circuit_composition :: CircuitComposition
        """
        number_layers =\
            len(self.composition.layers)
        number_cells ={
            layer: self.get_number_cells(layer)
            for layer in self.composition.layers}

        def __layer_gids_start_value(layer_index):
            return sum(number_cells[:layer_index + 1])

        cell_gids ={
            self.composition.layers[l]: [
                i + __layer_gids_start_value(l)
                for i in range(number_cells())
            }

