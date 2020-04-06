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
A mock circuit that we can use to test.
"""

import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields
from neuro_dmt.utils.geometry.roi import Cuboid
from .composition import CircuitComposition
from .connectivity import\
    CircuitConnectivity,\
    SimpleUniformRandomConnectivity,\
    SimpleUniformRandomConnectivityWithMtypeDependence
from .builder import CircuitBuilder
from .model import MockCircuitModel
from .adapter import MockCircuitAdapter
from .synapse import Synapse
from .cell import Cell

logger = Logger(client=__file__)
