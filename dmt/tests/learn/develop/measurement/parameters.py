"""Test develop  Parameter."""

import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random import RandomParameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.aggregate import ParameterAggregator
from dmt.vtk.measurement.parameter.group import get_grouped_values

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
class LayerModuloRandomNumber(Layer, RandomParameter):
    label="random"
    __type__=int
    def random_values(self, layer, *args, **kwargs):
        while True:
            yield np.random.randint(layer)

class LayerCellDensities(Layer, RandomParameter):
    label="cell_density"
    __type__=float

    def __init__(self, *args, **kwargs):
        self.cell_density = {1: 1.e0, 2: 1.e1, 3: 1.e2,
                             4: 1.e1, 5: 1.e2, 6: 1.e2}
        super(LayerCellDensities, self).__init__(*args, **kwargs)

    def random_values(self, layer, *args, **kwargs):
        while True:
            yield self.cell_density[layer]

    


layer_modulo = l.make_aggregator(LayerModuloRandomNumber())
layer_cell_density = l.make_aggregator(LayerCellDensities())


class HyperColumn(FiniteValuedParameter):
    """HyperColumn"""
    label = "hyper_column"
    value_type = int
    def __init__(self, *args, **kwargs):
        """..."""
        kwargs.update({
            "value_order": {i+1: i for i in range(7)},
            "representation": {i+1: "mc{}_Column".format(i+1) for i in range(7)}
        })
        super(HyperColumn, self).__init__(*args, **kwargs)


h = HyperColumn()


class CellDensityByLayerAndHyperColumn(RandomParameter):
    label = "cell_density"
    value_type = float
    def __init__(self, lh, *args, **kwargs):
        """
        Parameter
        ------------------------------------------------------------------------
        lh :: Record(
        ~    layer :: Layer,
        ~    hyper_column :: HyperColumn
        )
        """
        model = kwargs.get("model", None)
        self.cell_density = np.zeros([len(lh.layer.values),
                                      len(lh.hyper_column.values)])
        for l in lh.layer.values:
            for h in lh.hyper_column.values:
                self.cell_density[l-1, h-1]\
                    = model[l][h] if model else l * h * np.random.random()


    def random_values(self, lh, *args, **kwargs):
        l = lh.layer
        h = lh.hyper_column
        while True:
            yield self.cell_density[l-1][h-1] * np.random.random()


lhagg = ParameterAggregator((l, h,),
                            CellDensityByLayerAndHyperColumn(
                                Record(layer=l, hyper_column=h)
                            ))
