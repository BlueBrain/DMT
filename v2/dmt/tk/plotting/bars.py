"""
Bar plot.
"""

import pandas
import seaborn
from dmt.data.observation import measurement
from dmt.data.observation.measurement import get_samples
from dmt.tk.field import Field, LambdaField, lazyproperty
from .import golden_aspect_ratio
from .figure import Figure
from .import BasePlotter


class Bars(BasePlotter):
    """
    Specifies a plotting method, and all its required attributes.
    """
    @staticmethod
    def _get_phenomenon(dataframe_long):
        """
        Get phenomenon to be plotted.
        """
        return dataframe_long.columns[0]

    def _get_title(self, dataframe_long):
        """
        Get a title to display.
        """
        if self.title:
            return self.title
        phenomenon = self._get_phenomenon(dataframe_long)
        return ' '.join(word.capitalize() for word in phenomenon.split('_'))

    @classmethod
    def get_dataframe(cls, data):
        """..."""
        return data.reset_index()\
            if isinstance(data, (pandas.Series, pandas.DataFrame)) else\
               measurement.concat_as_samples(data).reset_index()\

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the dataframe.
        """
        graphic = seaborn\
            .catplot(
                data=self.get_dataframe(data),
                x=self.xvar,
                y=self.yvar,
                ci=self.confidence_interval,
                kind="bar",
                hue=self.gvar if self.gvar else None,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure)\
            .set(
                xlabel=self.xlabel,
                ylabel=self.ylabel,
                title=kwargs.pop("title", ""))
        return Figure(
            graphic,
            caption=caption)

    def plot(self,
            *args, **kwargs):
        """
        Plot the dataframe
         """
        return self.get_figure(*args, **kwargs)
