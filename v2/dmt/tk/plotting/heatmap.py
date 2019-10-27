"""
Plot heat maps.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from . import golden_aspect_ratio
from .figure import Figure
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, LambdaField, lazyproperty, WithFields

class HeatMap(WithFields):
    """
    Define the requirements and behavior of a heatmap.
    """
    xvar = Field(
        """
        Variable (column in the data-frame to plot) that should vary along the
        x-axis of the heat-map.
        """)
    yvar = Field(
        """
        Variable (column in the data-frame to plot) that should vary along the
        y-axis of the heat-map.
        """)
    vvar = Field(
        """
        Variable (column in the data-frame to plot) that provides the intensity
        value of the heat-map cells.
        """)
    xlabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `xvar` to be displayed
        as `xlabel`.
        """,
        lambda self: self.xvar)
    ylabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `yvar` to be displayed
        as `ylabel`.
        """,
        lambda self: self.yvar)
    height_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__ = 8.)
    aspect_ratio_figure = Field(
        """
        Aspect ratio width / height for the figure.
        """,
        __default_value__=1.)

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the figure.

        Arguments
        --------------
        `data`: A single pandas dataframe with an index of length 2, and only
        1 column (only the zeroth column will be plotted.)
        """
        assert isinstance(data, pandas.DataFrame) or len(data) == 1,\
            """
            Cannot decide which one to plot among more than one dataset:
            \t{}
            """.format(list(data.keys()))
        dataframe =\
            data if isinstance(data, pandas.DataFrame)\
            else list(data.values())[0]
        matrix = pandas\
            .pivot_table(
                data,
                values=self.vvar,
                index=self.xvar,
                columns=self.yvar)
        graphic = seaborn\
            .heatmap(
                matrix,
                cbar=True,
                cmap="rainbow",
                xticklabels=True,
                yticklabels=True)
        plt.yticks(rotation=0)
        plt.ylabel(self.ylabel)
        plt.xticks(rotation=90)
        plt.xlabel(self.xlabel)
        return Figure(
            graphic,
            caption=caption)
