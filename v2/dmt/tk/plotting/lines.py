"""
PLot lines.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.utils.string_utils import make_name
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from dmt.data.observation import measurement
from . import golden_aspect_ratio
from .figure import Figure


class LinePlot(WithFields):
    """
    Define the requirements and behavior of a line plot.
    """
    xvar = Field(
        """
        Column in the data-frame to be plotted along the x-axis.
        """)
    yvar= Field(
        """
        Column in the data-frame to be plotted along the y-axis.
        """)
    gvar = Field(
        """
        Geometry Variable: column in the dataframe that will be plotted as
        different geometries (i.e. lines for `LinePlot`).
        A default value of empty string will be interpreted as not set,
        and hence there will be only a single line in the plot.
        """,
        __default_value__="")
    fvar = Field(
        """
        Facet Variable: Column in the dataframe that will be plotted on several
        faces. A default value of empty string will be interpreted as not set,
        and hence there will be only one face in the figure.
        """,
        __default_value__="")
    xlabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `xvar` to be displayed.
        """,
        lambda self: self.xvar)
    ylabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `yvar` to be displayed.
        """,
        lambda self: self.yvar)
    height_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__=12.)
    aspect_ratio_figure = Field(
        """
        Aspect ratio width / height for the figure.
        """,
        __default_value__=golden_aspect_ratio)
    number_columns = LambdaField(
        """
        Number of columns in the figure.
        """,
        lambda self: None if not self.fvar else 3)
    drawstyle = Field(
        """
        Specify how to draw the lines that join the (x, y) points.
        Default value join the points with simple points. Other possibilities
        are steps.
        """,
        __default_value__="default")

    def get_dataframe(self, data, dataset=None):
        """
        Extract the dataframe to plot.
        """
        if dataset:
            raise NotImplementedError(
            """
                `LinePLot.get_figure(...)` current version does not support
                argument `dataset`.
                """)
        if isinstance(data, (pandas.Series, pandas.DataFrame)):
            return data.reset_index()
        return measurement.concat_as_samples(data).reset_index()

    def get_figure(self,
            data,
            *args,
            dataset=None,
            caption="Caption not provided"):
        """
        Plot the data.

        Arguments
        -------------
        data : Either a dataframe or a dict mapping dataset to dataframe.
        dataset : dataset or list of dataset names whose data will be plotted.
        """
        def _make_name(label):
            return make_name(
                '_'.join(label) if isinstance(label, tuple) else label,
                separator='_')

        grid = seaborn\
            .FacetGrid(
                self.get_dataframe(data, dataset),
                col=self.fvar if self.fvar else None,
                hue=self.gvar if self.gvar else None,
                col_wrap=self.number_columns,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure,
                legend_out=True)
        grid.map(
            seaborn.lineplot,
            self.xvar,
            self.yvar,
            drawstyle=self.drawstyle,
            alpha=0.7
        ).set_titles(
            _make_name(self.fvar) + "\n{col_name} "
        ).add_legend(
            title=_make_name(self.gvar))
        return Figure(
            grid.set(
                xlabel=self.xlabel,
                ylabel=self.ylabel),
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

    def __call__(self,
            data):
        """
        Make this class a callable,
        so that it can masquerade as a function!

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        return self.get_figure(*args, **kwargs)
