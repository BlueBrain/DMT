"""
Definitions and methods for cells of a MockCircuit.
"""

from dmt.tk.field import Field, WithFields
from . import CircuitComposition


class CircuitBuilder(WithFields):
    """
    Builds a circuit.
    """

    composition = Field(
        """
        Composition of the circuit.
        """,
        __type__=CircuitComposition)

    def get_number_cells(self, layer):
        """
        How many cells in a given layer?
        """
        volume =\
            self.composition.layer_thickness[layer] *\
            self.composition.column_base ** 2
        return int(
            self.composition.cell_density[layer] * volume)


    def place(self):
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
        number_cells =[
            self.get_number_cells(layer)
            for layer in self.composition.layers]

        def __layer_gids_start_value(layer_index):
            return sum(number_cells[:layer_index + 1])

        cell_gids = [
             i + __layer_gids_start_value(layer_index)
            for i in range(number_layers)
            for layer_index in range(number_layers)]


        
            
    
