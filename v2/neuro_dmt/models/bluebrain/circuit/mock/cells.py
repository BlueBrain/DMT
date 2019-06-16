"""
Definitions and methods for cells of a MockCircuit.
"""

import collections
from dmt.tk.field import Field, WithFields
from . import CircuitComposition


class CellProperty(Field):
    """
    Fully define a cell property,
    specifying the key to be used to index data-sets,
    its value type, and the set of values it may assume.
    """
    def __init__(self,
            __label__=None,
            __type__=object,
            __value_set__=set(),#empty means any value
            *args, **kwargs):
        """
        Initialize...
        """
        def __is_valid(instance, value):
            """
            Validate a value.

            Arguments
            -------------
            value :: Either a singleton, or an iterable.
            If 'value' is a singleton, it should be of the accepted type.
            If 'value' is an iterable (for e.g. a set of values), each
            of these values must be of the accepted type.
            """
            value_is_collection =\
                isinstance(value, collections.Iterable) and\
                not isinstance(value, (str, bytes))
            if __value_set__:
                if value_is_collection:
                    return all(
                        isinstance(v, __type__) and v in __value_set__
                        for v in value)
                return isinstance(value, __type__) and value in __value_set__
            if value_is_collection:
                return all(
                    isinstance(v, __type__)
                    for v in value)
            return isinstance(value, __type__)

        if __value_set__:
            self.__value_set__= emuset(*__value_set__)
        super().__init__(
            __is_valid_value__=__is_valid,
            *args, **kwargs)






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
    synapse_class = 



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


        
            
    
