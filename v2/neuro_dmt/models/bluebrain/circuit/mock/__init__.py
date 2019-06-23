"""
A mock circuit that we can use to test.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from .composition import CircuitComposition
from .builder import CircuitBuilder
from .circuit import MockCircuit

logger = Logger(client=__file__)
