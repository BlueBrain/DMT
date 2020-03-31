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
Fancy heatmap
by HD
"""
from matplotlib import pyplot as plt
from seaborn import heatmap
from dmt.tk.plotting import SeparatePlots
from dmt.tk.plotting.utils import \
    pivot_table, default_label_callback


# TODO: make it scale the size with the number on each
class HeatPlot(SeparatePlots):
    """
    draw a heatplot
    """

    def __init__(self, cmap='rainbow',
                 cbar=True, label_callback=default_label_callback):
        """
        Arguments:
            cmap: which color map to use for the heatplot
            cbar: whether to show a colorbar
            label_callback: a callback determining
                            the labels of groups in the matrix
                            recieves the parameter value for the group
                            and returns a string for the label
        """
        self.cmap = cmap
        self.cbar = cbar
        self.label_callback = label_callback
        return

    def plot(self, dataframe, values=None):
        """
        plot a heatplot for dataframe
        """
        import numpy as np
        kw = {'values': values} if values is not None else {}
        pvt, fg, tg = pivot_table(
            dataframe, label_callback=self.label_callback, **kw)
        f = plt.figure(figsize=np.array(pvt.shape) * 0.3)
        hm = heatmap(pvt, cmap=self.cmap, cbar=self.cbar,
                     xticklabels=True, yticklabels=True)
        return f
