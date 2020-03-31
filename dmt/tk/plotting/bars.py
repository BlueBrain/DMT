# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Bar plot.
"""

import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.journal import Logger
from dmt.data.observation import measurement
from dmt.data.observation.measurement import get_samples
from dmt.tk.field import Field, LambdaField, lazyproperty
from .import golden_aspect_ratio
from .figure import Figure
from .import BasePlotter

LOGGER = Logger(client=__file__)

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

    def get_dataframe(self, data):
        """..."""
        dataframe =\
            data.reset_index()\
            if isinstance(data, (pandas.Series, pandas.DataFrame)) else\
               measurement.concat_as_samples(data).reset_index()
        try:
            return self.order(dataframe)
        except TypeError:
            try:
                return dataframe.sort_values(by=self.order)
            except (TypeError, ValueError):
                LOGGER.warn(
                    """
                    Could not order dataframe to be plotted.
                    Using the dataframe as it is.
                    """)
        return dataframe

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
        plt.xticks(rotation=90)
        return Figure(
            graphic,
            caption=caption)


    def plot(self,
            *args, **kwargs):
        """
        Plot the dataframe
         """
        return self.get_figure(*args, **kwargs)
