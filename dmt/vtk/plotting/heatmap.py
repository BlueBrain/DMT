"""Plot a heat-map"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib\
    import pylab
from matplotlib.font_manager\
    import FontProperties
from dmt.vtk.utils.logging\
    import Logger
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting\
    import golden_figure\
    ,      Plot


class HeatMap(Plot):
    """Plot a heatmap."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self._logger=\
            Logger(
                self,
                level=Logger.level.DEBUG)
        self._index_values=\
            None
        self._dataframe = None
        self._matrix    = None
        super().__init__(
            *args, **kwargs)
        self._logger.debug(
            self._logger.get_source_info(),
            "data frame set? {}".format(self._dataframe))

    @property
    def dataframe(self):
        """We need dataframe in HeatMap in several places,
        so this property computes and saves the plotting dataframe."""
        if self._dataframe is None:
            self._dataframe=\
                self.get_plotting_dataframe(
                    allow_multi_indexed=True)
        return self._dataframe

    @property
    def index_values(self):
        """Get unique values for this instance's dataframe's index.
        Note that we expect the dataframe to be multi-indexed,
        and have only two levels each of which has the same 'value-type'.
        For example, the index may be (pre_mtype, post_mtype)."""
        if not self._index_values:
            dataframe=\
                self.get_plotting_dataframe(
                    allow_multi_indexed=True)
            if not isinstance(dataframe.index, pd.MultiIndex):
                raise ValueError(
                    "Plot dataframe {} is not a multi-indexed."\
                    .format(dataframe))
            if not len(dataframe.index.names) == 2:
                raise ValueError(
                    "Plot dataframe's index has more than 2 levels:\n {}"\
                    .format(dataframe.index))
            self._index_values=\
                sorted(list({
                    k for tup in dataframe.index.values for k in tup}))
        return self._index_values

    def axes_indexes(self,
            with_customization={}):
        """The data-frame used in HeatMap is assumed to contain (atleast)
        two columns. Which one should be along X and which along Y?
        """
        dataframe=\
            self.get_plotting_dataframe(
                allow_multi_indexed=True)
        index=\
            dataframe.index
        if not isinstance(index, pd.MultiIndex):
            raise ValueError(
                "Plot dataframe {} is not a multi-indexed."\
                .format(dataframe))
        x_label=\
            with_customization.get(
                "xvar",
                with_customization.get(
                    "x_var",
                    None))
        y_label=\
            with_customization.get(
                "y_var",
                with_customization.get(
                    "yvar",
                    None))
        x_index=\
            dataframe.index.names.index(x_label)\
            if x_label else None
        y_index=\
            dataframe.index.names.index(y_label)\
            if y_label else None
        if not (x_index or y_index):
            return (0, 1)
        if x_index and y_index:
            assert x_index != y_index
            return (x_index, y_index)
        if x_index:
            assert x_index == 0 or x_index == 1
            return (x_index, 1 - x_index)
        assert y_index == 0 or y_index == 1
        return (1 - y_index, y_index)
    
    def axes_ordered(self,
            x_value,
            y_value,
            with_customization={}):
        """The dataframe used in HeatMap is assumed to contain (atleast)
        two columns. Which one should be along X and which along Y?
        We assume that the dataframe's index is 0 --> 1, if there is any sense
        of direction involved (as is the case pre-synaptic --> post_synaptic.)
        """
        x_index, y_index=\
            self.axes_indexes(
                with_customization)
        if x_index == 0:
            return (x_value, y_value)
        return (y_value, x_value)

    def _get_value(self,
            x, y,
            column="mean",
            with_customization={}):
        """Get value for index (x, y)."""
        u,v=\
            self.axes_ordered(
                x,y,
                with_customization)
        return\
            self.dataframe\
                .loc[(u,v)][column]\
            if (u,v) in self.dataframe.index else\
               np.nan

    def matrix(self,
            with_customization={}):
        """To make a heat-map we need a matrix."""
        try:
            return\
                np.array([
                    [self._get_value(
                        x, y,
                        column="mean",
                        with_customization=with_customization)
                         for x in self.index_values]
                        for y in self.index_values])
        except ValueError as value_error:
            error_message=\
                """{}
                Does the plotting dataframe have a degenerate index?"""\
                    .format(value_error)
            self._logger.alert(
                self._logger.get_source_info(),
                """Caught ValueError {} """.format(value_error),
                """Does the plotting dataframe have a degenerate index?""")
            raise ValueError(
                error_message)
        return None

    def get_color_limits(self,
            with_customization={
                "use_logscale": False}):
        """..."""
        return(
            np.nanmin(self.matrix(with_customization)),
            np.nanmax(self.matrix(with_customization)))

    def plot(self,
            with_customization={}):
        """..."""
        figure=\
            golden_figure(
                height=self._height,
                width=self._width)
        axes=\
            figure.add_axes(
                [0.075, 0.125, 0.9, 0.8])
        image=\
            axes.imshow(
                self.matrix(with_customization),
                interpolation="nearest")
        index_values=\
            self._index_values
        n_data_points=\
            len(index_values)
        x_index, y_index=\
            self.axes_indexes(
                with_customization)
        axes.set_xlabel(
            self.dataframe.index.names[x_index])
        axes.set_xticks(
            range(n_data_points))
        axes.set_xticklabels(
            index_values,
            rotation="vertical",
            size="xx-small")
        axes.set_ylabel(
            self.dataframe.index.names[y_index])
        axes.set_yticks(
            range(n_data_points))
        axes.set_yticklabels(
            index_values,
            size="xx-small")
        color_limits=\
            with_customization.get(
                "color_limits",
                self.get_color_limits(
                    with_customization))
        image.set_clim(
            color_limits[0],
            color_limits[1])
        colorbar=\
            plt.colorbar(
                image)
        return figure
