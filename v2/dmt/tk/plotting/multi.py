"""
Generate several plots.
"""
from collections import OrderedDict
import pandas
import seaborn
from dmt.tk.field import Field, lazyfield, WithFields

class MultiPlot(WithFields):
    """
    Using a plotter-type instance, create several plots, that will be
    returned in a dictionary.
    """
    plotter = Field(
        """
        Plotter type instance.
        """)
    mvar = Field(
        """
        Multi-plot variable.
        Name of the column in the dataframes to be plotted that will be varied
        to subset the data, feed it to `self.plotter` to get individual plots
        for the values of `mvar`.
        """)

    def get_figures(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Returns
        ================
        OrderedDict mapping value of `self.mvar` to its plot.
        """

        def _get_sub_figure(dataframe_subset):
            """..."""
            return self.plotter.get_figure(
                dataframe_subset,
                *args,
                caption=caption
            )

        dataframe = self.plotter.get_dataframe(data)
        return dataframe.groupby(
            self.mvar
        ).apply(
            _get_sub_figure
        ).to_dict()
