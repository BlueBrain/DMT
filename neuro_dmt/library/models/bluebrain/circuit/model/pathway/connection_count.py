# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Count the number of connections in a pathway
"""

import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import lazyfield
from .connection_probability import ConnectionProbability

logger = Logger(client=__file__)

class ConnectionStrength(ConnectionProbability):
    """
    Count the number of connections in a pathway
    """
    phenomenon = "connection_strength"
    aggregators_inner = ["sum"]
    aggregators_outer = ["size", "mean", "std"]
    measurement_label = "connection_strength"
    columns = {"sum": "connection_strength"}

    @lazyfield
    def definition(self):
        """..."""
        return {}


class AfferentConnectionStrengthBySomaDistance(
        ConnectionProbabilityByDistance):
    """..."""
    phenomenon = "Afferent Connections"
    aggregators_inner = ["sum"]
    aggregators_outer = ["size", "mean", "std"]
    measurement_label = "afferent_connections"
    columns = {"sum": "afferent_connections"}

    @property
    def definition(self):
        return {}
