# Copyright (c) 2019, EPFL/Blue Brain Project

# This file is part of BlueBrain SNAP library <https://github.com/BlueBrain/snap>

# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
# by the Free Software Foundation.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Neuroscience experimental data.
"""
from collections import OrderedDict
from dmt.tk.phenomenon import Phenomenon
from dmt.data.observation import SampleMeasurement, Summary

class ByLayerCellDensityMeasurement(SampleMeasurement):
    """
    Measurement of cell density, by cortical layer.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        description="Count of cells per unit volume.",
        group="Composition")
    parameters = OrderedDict(
        layer="Cortical layer where to count the cells in.")


class ByLayerInhibitoryCellFractionMeasurement(SampleMeasurement):
    """
    Measurement of inhibitory cell fraction, by cortical layer.
    """
    phenomenon = Phenomenon(
        "Inhibitory Cell Fraction",
        description="Fraction of inhibitory cells in a population.",
        group="Composition")
    parameters = OrderedDict(
        layer="Cortical layer where the inhibitory cell fraction was measured.")
