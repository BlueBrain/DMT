"""
Plot heat maps.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from . import golden_aspect_ratio
from .figure import Figure
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, lazyproperty, WithFields

class HeatMap(WithFields):
    """
    Define the requirements and behavior of a heatmap.
    """
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
            dataframe,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the figure.

        Arguments
        --------------
        `dataframe`: A single pandas dataframe with an index of length 2, and only
        1 column (only the zeroth column will be plotted.)
        """
        matrix = pandas\
            .pivot_table(
                dataframe,
                values=dataframe.columns[0],
                index=dataframe.index.names[0],
                columns=dataframe.index.names[1])
        graphic = seaborn\
            .heatmap(
                matrix,
                cbar=True,
                cmap="rainbow",
                xticklabels=True,
                yticklabels=True)
        plt.yticks(rotation=0)
        plt.xticks(rotation=90)
        return Figure(
            graphic,
            caption=caption)
