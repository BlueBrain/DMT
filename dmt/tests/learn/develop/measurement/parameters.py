"""Test develop  Parameter."""

import numpy as np
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate, get_conditioned_random_variate
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement import StatisticalMeasurement

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

layer = Layer()
class LayerModuloRandomNumber(ConditionedRandomVariate):
    label="random"
    __type__=int
    def __init__(self, scale):
        self.scale = scale
        super(LayerModuloRandomNumber, self)\
            .__init__(conditioning_variables = (Layer(),))

    def values(self, condition, *args, **kwargs):
        self.assert_condition_is_valid(condition)
        while True:
            yield self.scale * np.random.randint(condition.layer)


def lm_random(condition, *args, **kwargs):
    assert(hasattr(condition, "layer"))
    while True:
        yield kwargs.get("scale", 1.0) * np.random.randint(condition.layer)

class LayerCellDensity(ConditionedRandomVariate):
    label="cell_density"
    __type__=float

    def __init__(self, std=1., *args, **kwargs):
        self.cell_density_mean = {1: 1.e0, 2: 1.e1, 3: 1.e2,
                                  4: 1.e1, 5: 1.e2, 6: 1.e2}
        self.cell_density_std  = std
        super(LayerCellDensity, self).__init__(conditioning_variables=(Layer(),))

    def values(self, condition, *args, **kwargs):
        self.assert_condition_is_valid(condition)
        while True:
            yield np.random.normal(self.cell_density_mean[condition.layer],
                                   self.cell_density_std)

class CellDensityModel(RandomVariate):
    label = "cell_density"
    value_type = float
    def __init__(self, *args, **kwargs):
        """a model with sigma 1"""
        stdev = kwargs.get("stdev", 1.0)
        self.cell_density_mean = {1: 1.e0, 2: 1.e1, 3: 1.e2,
                                  4: 1.e1, 5: 1.e2, 6: 1.e2}
        self.cell_density_std  = stdev

    def values(self, condition, *args, **kwargs):
       """...""" 
       assert(hasattr(condition, "layer"))
       while True:
           yield max(np.random.normal(self.cell_density_mean[condition.layer],
                                      self.cell_density_std),
                     0.0)



layer_modulo = LayerModuloRandomNumber(1.0)
layer_module_fly = layer.make_aggregator(lm_random)
layer_cell_density = LayerCellDensity()
layer_cell_density_fly = layer.make_aggregator(CellDensityModel(1.0).values)


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


hyper_column = HyperColumn()

class CellDensityByLayerAndHyperColumn(RandomVariate):
    label = "cell_density"
    value_type = float
    def __init__(self, *args, **kwargs):
        """
        """
        model = kwargs.get("model", None)
        self.cell_density = np.zeros([len(layer.values),
                                      len(hyper_column.values)])
        for l in layer.values:
            for h in hyper_column.values:
                self.cell_density[l-1, h-1]\
                    = model[l][h] if model else l * h * np.random.random()

        super(CellDensityByLayerAndHyperColumn, self).__init__(*args, **kwargs)


    def values(self, condition, *args, **kwargs):
        """..."""
        l = condition.layer
        h = condition.hyper_column
        while True:
            yield max(self.cell_density[l-1][h-1] * np.random.random(), 0.0)

class RegionOfInterestByLayerAndHyperColumn(RandomVariate):
    """..."""
    label = "roi"
    value_type = float
    def __init__(self, *args, **kwargs):
        super(RegionOfInterestByLayerAndHyperColumn, self).__init__(*args, **kwargs)

    def values(self, condition, *args, **kwargs):
        yield condition.layer * condition.hyper_column * np.random.random()


from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
class RandomCellDensity(measurement.Method):
    """..."""
    label = "cell_density"
    phenomenon = Phenomenon("cell_density", "count of cells in a unit volume")
    units = "1"
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, roi):
            return roi * np.random.random()



sm = StatisticalMeasurement(method=RandomCellDensity(),
                            by=get_conditioned_random_variate(
                                (layer, hyper_column,),
                                RegionOfInterestByLayerAndHyperColumn()
                            ))

