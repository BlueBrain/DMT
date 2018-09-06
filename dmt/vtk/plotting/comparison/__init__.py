"""Plotting for comparisons."""
from abc import abstractmethod
from dmt.vtk.plotting import Plot
from dmt.vtk.utils.collections import Record

class ComparisonPlot(Plot):
    """Abstract base class for Specialized Plot for a comparison."""
    def __init__(self, data, *args, **kwargs):
        """Will compare data 'data'.

        Parameters
        ------------------------------------------------------------------------
        data :: Either[ DataFrame[mean :: Double, std  :: Double],
        ~               DataFrame[mean :: Double] ]
        """
        self._data_record = data
        self._data = data.data
        self._label = data.label
        self._comparison_level = kwargs.get("level", None)
        self._comparison_data = kwargs.get("comparison_data", None)
        self._given_vars = kwargs.get("given", None)
        self._compared_values = kwargs.get("compared_values", None)
        super(ComparisonPlot, self).__init__(*args, **kwargs)

    def against(self, datasets, given=None):
        """Compare data against..."""
        if self._comparison_level is None:
            raise(TypeError("{}'s comparison_level not specified."\
                            .format(self.__class__)))
        self._comparison_data=datasets
        self._given_vars = given
        return self

    def comparing(self, level):
        """..."""
        self._comparison_level = level
        return self

    def for_given(self, given):
        """..."""
        if self._comparison_data is None:
            raise TypeError("{}'s comparison_data not specified.".\
                            format(self.__class__))
        return self.against(self._comparison_data, given=given)

    @property
    def compared_values(self):
        if self._compared_values:
            return self._compared_values
        else:
            idx = self._comparison_data.index
            names = idx.levels[idx.names.index(self._comparison_level)]
            return [Record(name=name, label=name) for name in names]

