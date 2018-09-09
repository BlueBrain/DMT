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

    def against(self, datasets, given=()):
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

    def for_given(self, *given):
        """..."""
        if self._comparison_data is None:
            raise TypeError("{}'s comparison_data not specified.".\
                            format(self.__class__))
        return self.against(self._comparison_data, given=given)

    def level_values(self, level=None):
        if not level:
            return None
        idx = self._comparison_data.index
        return idx.levels[idx.names.index(level)]

    @property
    def compared_values(self):
        if self._compared_values:
            return self._compared_values
        return (Record(name=name, label=name)
                for name in self.level_values(self._comparison_level))

    @property
    def given(self):
        """self._given_vars may be an iterable."""
        try:
            return self._given_vars[0]

        except:
            pass

        return self._given_vars

    @property
    def given_var_values(self):
        """Values of the 'given' vars that will be plotted."""
        g = self.given
        return self._data.index if not g else self.level_values(g)
               
