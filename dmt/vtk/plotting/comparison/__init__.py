"""Plotting for comparisons."""
from abc import abstractmethod
import pandas as pd
from dmt.vtk.plotting import Plot
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.exceptions import ValueNotSetError
from dmt.vtk.measurement.parameter import Parameter

class ComparisonPlot(Plot):
    """Abstract base class for Specialized Plot for a comparison."""
    def __init__(self,
            measurement,
            *args, **kwargs):
        """Will compare data 'data'.

        Parameters
        ------------------------------------------------------------------------
        data :: Either[ DataFrame[mean :: Double, std  :: Double],
        ~               DataFrame[mean :: Double] ]
        """
        self._comparison_level=\
            kwargs.get(
                "level", None)
        self._comparison_data=\
            kwargs.get(
                "comparison_data", None)
        self._given_vars=\
            kwargs.get(
                "given",
                measurement.data.index.name)
        self._compared_values=\
            kwargs.get(
                "compared_values", None)
        super().__init__(
            measurement,
            *args, **kwargs)

    def against(self,
            datasets,
            comparing="dataset"):
        """Compare data against..."""
        if not isinstance(datasets.index, pd.MultiIndex):
            assert isinstance(datasets.index, pd.Index)
            datasets.index=\
                pd.MultiIndex.from_tuples(
                    tuples=[("reference", i) for i in datasets.index],
                    names=["dataset", datasets.index.name])
        self._comparison_data=\
            datasets
        self._comparison_level=\
            comparing
        return self

    def with_xvar(self,
            variable):
        """..."""
        if self._comparison_level is None:
            raise Exception(
                "{}'s comparison_level not specified."\
                .format(
                    self.__class__))
        variable_label=\
            getattr(variable, "label", variable)
        if variable_label not in self._data.index.names:
            raise\
                Exception(
                    """Label of the 'given' var '{}' is
                    not in {}'s data's index.  Please choose from {}."""\
                    .format(
                        variable_label, self,
                        self._data.index.names))
        if variable_label not in self._comparison_data.index.names:
            raise\
                Exception(
                    """Label of the 'given' var '{}' is not in {}'s
                    comparison_data's index. Please choose from {}."""\
                    .format(
                        variable_label, self,
                        self._comparison_data.index.names))

        self._xvar = variable_label
        return self

    def level_values(self,
            level=None):
        """..."""
        if not level:
            return None
        idx = self._comparison_data.index
        return idx.levels[idx.names.index(level)]

    @property
    def comparison_data(self):
        """..."""
        if self._comparison_data is None:
            raise ValueError(
                "{} has no comparison data!".format(self))
        return self._comparison_data

    @property
    def comparison_level(self):
        """..."""
        if self._comparison_level is None:
            self._logger.alert(
                self._logger.get_source_info(),
                "{}'s _comparison_level not set".format(self))
            return "dataset"
        return self._comparison_level
    
    @property
    def compared_values(self):
        """..."""
        if self._compared_values:
            return self._compared_values
        return [
            Record(name=name, label=name)
            for name in self.level_values(
                    self.comparison_level)]

    @property
    def xvar_values(self):
        """Values of the 'given' vars that will be plotted."""
        if isinstance(self._xvar, Parameter):
            g = self._xvar.label
            return\
                self._data.index if not g else\
                [self._xvar.repr(v) for v in self.level_values(g)]
        return[
            str(v) for v in self.level_values(self._xvar)]
               

from dmt.vtk.plotting.comparison.barplot\
    import BarPlotComparison
from dmt.vtk.plotting.comparison.crossplot\
    import CrossPlotComparison
