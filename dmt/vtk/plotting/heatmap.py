"""Plot a heat-map"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib\
    import pylab
from matplotlib.font_manager\
    import FontProperties
from dmt.vtk.plotting\
    import golden_figure\
    ,      Plot


class HeatMap(Plot):
    """Plot a heatmap."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        self._index_values=\
            None
        super().__init__(
            *args, **kwargs)


    @property
    def index_values(self):
        """Get unique values for this instance's dataframe's index.
        Note that we expect the dataframe to be multi-indexed,
        and have only two levels each of which has the same 'value-type'.
        For example, the index may be (pre_mtype, post_mtype)."""
        if not self._index_values:
            dataframe=\
                self.get_dataframe(
                    allow_multi_indexed=True)
            if not isinstance(dataframe.index, pd.MultiIndex):
                raise ValueError(
                    "Plot dataframe is not a multi-indexed.")
            if not len(dataframe.index.names) == 2:
                raise ValueError(
                    "Plot dataframe's index has more than 2 levels:\n {}"\
                    .format(dataframe.index))
            self._index_values=\
                list({k for tup in dataframe.index.values for k in tup})

        return self._index_values

    @property
    def matrix(self):
        """To make a heat-map we need a matrix."""
        dataframe=\
            self.get_dataframe(
                allow_multi_indexed=True)
        return\
            np.array(
                [[dataframe.loc[(x, y)]["mean"]
                  for x in self.index_values]
                 for y in self.index_values])

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
                self.matrix,
                interpolation="nearest")
        index_values=\
            self._index_values
        n_data_points=\
            len(index_values)
        axes.set_xticks(
            range(n_data_points))
        axes.set_xticklabels(
            index_values,
            rotation="vertical",
            size="xx-small")
        axes.set_yticks(
            range(n_data_points))
        axes.set_yticklabels(
            index_values,
            size="xx-small")
        color_limits=\
            with_customization.get(
                "color_limits",
                getattr(self,
                    "color_limits",
                    (0, np.log10(0.05))))
        image.set_clim(
            color_limits[0],
            color_limits[1])
        colorbar=\
            plt.colorbar(
                image)
        return figure
