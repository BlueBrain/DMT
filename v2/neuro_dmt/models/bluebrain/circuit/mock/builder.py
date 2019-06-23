"""
Build a mock circuit.
"""

from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.field import Field, WithFields

from ..geometry import Position
from .cell import Cell
from .composition import CircuitComposition
from .connectivity import CircuitConnectivity



MTYPE = CellProperty.MTYPE
REGION = CellProperty.REGION
LAYER = CellProperty.LAYER


class CircuitBuilder(WithFields):
    """
    Builds a circuit.
    """

    composition = Field(
        """
        An object parameterizing the circuit's composition.
        """,
        __type__=CircuitComposition)
    connectivity = Field(
        """
        An object parameterizing the circuit's connectivity.
        """,
        __type__=CircuitConnectivity)

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
        return\
            self.composition\
                .cell_density.xs(
                    (region, layer, mtype) if region else (layer, mtype),
                    level=(REGION, LAYER, MTYPE) if region else (LAYER, MTYPE))

    def get_number_cells(self, layer, mtype, region=None):
        """
        How many cells of given 'mtype' in a given 'layer'?
        """
        volume =\
            self.composition.thickness_layer[layer] *\
            self.composition.length_base ** 2
        density =\
            self.get_cell_density(
                region, layer, mtype)["mean"]
        return int(1.e-9 * density * volume)

    def get_cells(self):
        """
        Create cells for each layer and mtype combination.
        """
        return [
            Cell(
                layer=layer,
                position=Position.sample(
                    self.composition.bounding_box(layer, mtype)),
                mtype=mtype)
            for layer in self.composition.layers
            for mtype in self.composition.mtypes
            for _ in range(self.get_number_cells(layer, mtype))]
