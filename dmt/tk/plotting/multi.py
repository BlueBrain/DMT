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
Generate several plots.
"""
from copy import deepcopy
from collections import OrderedDict
import pandas
import seaborn
from dmt.tk.utils.string_utils import make_name
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

    def _get_sub_figure(self,
            value_mvar,
            dataframe_subset,
            caption,
            *args, **kwargs):
        """..."""
        name_mvar =\
            make_name(
                '_'.join(self.mvar) if isinstance(self.mvar, tuple) else self.mvar,
                separator='_')
        plotter = deepcopy(self.plotter)
        return plotter.get_figure(
            dataframe_subset,
            *args,
            caption=caption,
            title="{} {}".format(self.mvar, value_mvar),
            **kwargs)

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

        dataframe = self.plotter.get_dataframe(data)
        values_mvar = dataframe[self.mvar].unique()
        return OrderedDict([
            (value_mvar,
             self._get_sub_figure(
                 value_mvar,
                 dataframe[dataframe[self.mvar] == value_mvar],
                 caption,
                 *args, **kwargs))
             for value_mvar in values_mvar])


    def __call__(self, *args, **kwargs):
        """
        Behave like a Plotter.
        """
        return self.get_figures(*args, **kwargs)
