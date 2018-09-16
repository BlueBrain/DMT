"""Test develop  Parameter."""

import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random import RandomParameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter

class Layer(FiniteValuedParameter):
    """Layer"""
    label = "layer"
    value_type = int
    def __init__(self, *args, **kwargs):
        """..."""
        kwargs.update({
            "value_order": {i+1: i for i in range(6)},
            "representation": {1: "I", 2: "II", 3: "III",
                               4: "IV", 5: "V", 6: "VI"}
        })
        super(Layer, self).__init__(*args, **kwargs)


l = Layer()
class LayerModuleRandomNumber(Layer, RandomParameter):
    label="random"
    __type__=int
    def random_values(self, layer, *args, **kwargs):
        while True:
            yield np.random.randint(layer)



lagg = l.make_aggregator(LayerModuleRandomNumber())
