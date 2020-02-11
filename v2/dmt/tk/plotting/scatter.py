"""
PLot lines.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.utils.string_utils import make_name
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.data.observation import measurement
from . import golden_aspect_ratio
from  .import BasePlotter
from .figure import Figure


class ScatterPlot(BasePlotter):
    """
    Define the requirements and behavior of a line plot.
    """
    labels_xticks = Field(
        """
        Point type to be plotted.
        """,
        __default_value__="")
    gvar_order = Field(
        """
        An order on group variables, 
        """,
        __default_value__=[])
    gvar_kwargs = Field(
        """
        Customize plotting of group variable data.
        """,
        __default_value__={})
    markers = Field(
        """
        Size of the markers.
        """,
        __default_value__={})
    svar = Field(
        """
        Variable in the dataframe to determine style of the scattered points.
        """,
        __default_value__="")
    size_markers = Field(
        """
        Size for all markers
        """,
        __default_value__=40)

    def get_dataframe(self, data, dataset=None):
        """
        Extract the dataframe to plot.
        """
        if dataset:
            raise NotImplementedError(
            """
                `ScatterPlot.get_figure(...)` current version does not support
                argument `dataset`.
                """)
        if isinstance(data, (pandas.Series, pandas.DataFrame)):
            return data.reset_index()
        return measurement.concat_as_samples(data).reset_index()

    def get_figure(self,
            data,
            *args,
            dataset=None,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the data.

        Arguments
        -------------
        data : Either a dataframe or a dict mapping dataset to dataframe.
        dataset : dataset or list of dataset names whose data will be plotted.
        """
        self._set_rc_params()
        plt.figure(
            figsize=(self.aspect_ratio_figure * self.height_figure,
                     self.height_figure))
        def _make_name(label):
            return make_name(
                '_'.join(label) if isinstance(label, tuple) else label,
                separator='_')
        dataframe =\
            self.get_dataframe(data, dataset)
        # grid = seaborn\
        #     .FacetGrid(
        #         dataframe,
        #         col=self.fvar if self.fvar else None,
        #         hue=self.gvar if self.gvar else None,
        #         hue_order=self.gvar_order if self.gvar_order else None,
        #         hue_kws=self.gvar_kwargs if self.gvar_kwargs else None,
        #         col_wrap=self.number_columns,
        #         height=self.height_figure,
        #         aspect=self.aspect_ratio_figure,
        #         legend_out=True)
        # grid.map(
        #     seaborn.scatterplot,
        #     self.xvar,
        #     self.yvar,
        #     style=self.svar if self.svar else None,
        #         markers=self.markers if self.markers else None,
        #     alpha=0.7
        # ).set_titles(
        #     _make_name(self.fvar) + "\n{col_name} "
        # ).add_legend(
        #     title=_make_name(self.gvar))
        # graphic =\
        #     grid.set(
        #         xlabel=self.xlabel,
        #         ylabel=self.ylabel,
        #     title=self.title)
        graphic =\
            seaborn.scatterplot(
                x=self.xvar,
                y=self.yvar,
                style=self.svar,
                markers=self.markers,
                hue=self.gvar,
                data=dataframe,
                s=self.size_markers)
        graphic.set(
                xlabel=self.xlabel,
                ylabel=self.ylabel)
        return Figure(
            graphic,
            caption=caption)

    def plot(self,
            *args, **kwargs):
        """
        Plot the data

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        return self.get_figure(*args, **kwargs)

