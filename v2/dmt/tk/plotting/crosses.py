"""
Plot crosses to compare two datasets.
"""

import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import seaborn
from dmt.data.observation import measurement
from dmt.tk.field import Field, lazyfield, WithFields
from .import golden_aspect_ratio
from .figure import Figure

class Crosses(WithFields):
    """
    A plot that compares measurements of a phenomena across two datasets.
    """
    title = Field(
        """
        Title to be displayed.
        If not provided phenomenon for the data will be used.
        """,
        __default_value__="")
    xvar = Field(
        """
        Name of the dataset whose values will be plotted along the x-axis.
        """)
    yvar = Field(
        """
        Name of the dataset whose values will be plotted along the y-axis.
        """)
    gvar = Field(
        """
        Column name that provides values of the measurement parameter used for
        each row of the dataframe that will be plotted.
        For example, consider PSP amplitude measurements made for several
        mtype -> mtype pathways. In this case `gvar` will be `pathway`.
        """)
    xlabel = Field(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `xvar` to be displayed
        as `xlabel`.
        """,
        __default_value__="")
    ylabel = Field(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `yvar` to be displayed
        as `ylabel`.
        """,
        __default_value__="")
    fmt = Field(
        """
        Point type to be plotted.
        """,
        __default_value__='o')
    size_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__ = 8.)

    @lazyfield
    def xerr(self):
        """
        Column that will contain errors associated with `xvar`.
        """
        return "{}_err".format(self.xvar)

    @lazyfield
    def yerr(self):
        """
        Column that will contain errors associated with `yvar`.
        """
        return "{}_err".format(self.yvar)

    @staticmethod
    def _get_phenomenon(dataframe_long):
        """
        Get phenomenon to be plotted.
        """
        return dataframe_long.columns[0][0]

    def _get_plotting_data(self, dataframe_long):
        """
        Convert `data` to plotting data.
        """
        datasets =\
            dataframe_long.reset_index().dataset.unique()
        if len(datasets) != 2:
            raise TypeError(
                """
                Dataframe for plotting has more than two datasets: {}
                """.format(datasets))
        phenomenon =\
            self._get_phenomenon(dataframe_long)
        dataframe_x =\
            dataframe_long.xs(self.xvar, level="dataset")[phenomenon]\
                     .dropna()
        dataframe_y =\
            dataframe_long.xs(self.yvar, level="dataset")[phenomenon]\
                     .dropna()
        if dataframe_x.shape[0] != dataframe_y.shape[0]:
            raise TypeError(
                """
                Dataframe for plotting had different number of elements
                for the two datasets to be plotted:
                {}: {}
                {}: {}
                """.format(
                    self.xvar, dataframe_x.shape[0],
                    self.yvar, dataframe_y.shape[0]))
        return\
            pd.DataFrame(
                {self.xvar: dataframe_x["mean"].values,
                 self.yvar: dataframe_y["mean"].values,
                 self.xerr: dataframe_x["std"].values,
                 self.yerr: dataframe_y["std"].values},
                index=dataframe_x.index)\
              .reset_index()

    def _get_title(self, dataframe_long):
        """
        Get a title to display.
        """
        if self.title:
            return self.title
        phenomenon = self._get_phenomenon(dataframe_long)
        return ' '.join(word.capitalize() for word in phenomenon.split('_'))

    def get_dataframe(self, data):
        """..."""
        return data\
            if isinstance(data, (pd.Series, pd.DataFrame)) else\
               measurement.concat_as_summaries(data).reset_index())
        
    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the data.

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        dataframe_long = self.get_dataframe(data)
        dataframe_wide = self._get_plotting_data(dataframe_long)
        graphic =\
            seaborn.FacetGrid(
                dataframe_wide,
                hue=self.gvar,
                size=self.size_figure,
                legend_out=True)
        graphic.map(
            plt.errorbar,
            self.xvar,
            self.yvar,
            self.xerr,
            self.yerr,
            fmt=self.fmt)
        graphic.add_legend()
        graphic.fig.suptitle(self._get_title(dataframe_long))
        limits =[
            np.maximum(
                np.nanmax(
                    dataframe_wide[self.xvar] + dataframe_wide[self.xerr]),
                np.nanmax(
                    dataframe_wide[self.yvar] + dataframe_wide[self.yerr])),
            np.minimum(
                np.nanmin(
                    dataframe_wide[self.xvar] - dataframe_wide[self.xerr]),
                np.nanmin(
                    dataframe_wide[self.yvar] - dataframe_wide[self.yerr]))]
        plt.plot(limits, limits, "k--")
        return Figure(
            graphic.set(
                xlabel=self.xlabel if self.xlabel else self.xvar,
                ylabel=self.ylabel if self.ylabel else self.yvar),
            caption=caption)

    def plot(self,
            data,
            *args, **kwargs):
        """
        Plot the data

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        return self\
            .get_figure(
                dataframe,
                *args, **kwargs)

    def __call__(self,
            data):
        """
        Make this class a callable,
        so that it can masquerade as a function!

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        return self.plot(data)
