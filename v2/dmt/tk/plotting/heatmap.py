"""
Plot heat maps.
"""
import pandas
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

    def __hplot(self, data, label):
        """
        Make a heat map.
        """
        df_matrix, _, __ = pivot_table(df, PRESYNAPTIC, POSTSYNAPTIC, MEAN,
                                  value_callback=custom_label_callback)
        height = self.height_figure
        width = self.aspect_ratio_figure * height
        fig, ax = plt.subplots(figsize=(width, height))
        seaborn.heatmap(
            df_matrix,
            cbar=True, cmap='rainbow', xticklabels=True, yticklabels=True)
        return fig

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the figure.
        """
        graphic = self.
        return Figure(
            graphic.set(
                xlabel=self.xlabel if self.xlabel else self.xvar,
                ylabel=self.ylabel if self.ylabel else self.yvar),
            caption=caption)
