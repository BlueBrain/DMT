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
            data,
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
                data.data.index.name)
        self._compared_values=\
            kwargs.get(
                "compared_values", None)
        super().__init__(
            data,
            *args, **kwargs)

    def against(self,
            datasets,
            given=()):
        """Compare data against..."""
        if not isinstance(datasets.index, pd.MultiIndex):
            assert isinstance(datasets.index, pd.Index)
            datasets.index=\
                pd.MultiIndex.from_tuples(
                    tuples=[("reference", i) for i in datasets.index],
                    names=["dataset", datasets.index.name])
        self._comparison_data= datasets
        if given: 
            self._given_vars = given
        return self

    def comparing(self,
            level):
        """..."""
        if self._comparison_data is None:
            raise Exception(
                """{}'s comparison_data (reference data to compare against)
                not set.""".format(self.__class__))
        self._comparison_level = level
        return self

    def for_given(self,
            *given):
        """..."""
        if self._comparison_level is None:
            raise Exception(
                "{}'s comparison_level not specified."\
                .format(self.__class__))
        for g in given:
            g_label=\
                getattr(g, "label", g)
            if g_label not in self._data.index.names:
                raise Exception(
                    """Label of the 'given' var '{}' is not in {}'s data's index.
                    Please choose from {}."""\
                    .format(
                        g_label, self,
                        self._data.index.names))
            if g_label not in self._comparison_data.index.names:
                raise Exception(
                    """Label of the 'given' var '{}' is not in {}'s
                     comparison_data's index. Please choose from {}."""\
                    .format(
                        g_label, self,
                        self._comparison_data.index.names))
        return\
            self.against(
                self._comparison_data,
                given=given)

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
            self.logger.alert(
                self.logger.get_source_info(),
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
    def given(self):
        """self._given_vars may be an iterable."""
        if isinstance(self._given_vars, (list, tuple)):
            return self._given_vars[0]
        return self._given_vars

    @property
    def given_variable_values(self):
        """Values of the 'given' vars that will be plotted."""
        if isinstance(self.given, Parameter):
            g = self.given.label
            return (
                self._data.index if not g else
                [self.given.repr(v) for v in self.level_values(g)])
        return[
            str(v) for v in self.level_values(self.given)]
               

from dmt.vtk.plotting.comparison.barplot\
    import BarPlotComparison
from dmt.vtk.plotting.comparison.crossplot\
    import CrossPlotComparison
