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
