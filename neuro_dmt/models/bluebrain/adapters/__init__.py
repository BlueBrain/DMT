"""Common code for all BBP circuit adapters, using the bluepy API.

"""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell

class BlueBrainModelAdapter:
    """Base class that provides code common to all brain circuit models from
    the Blue Brain Project."""

    def __init__(self, *args, **kwargs):
        """Initialize common attributes"""
        super(BlueBrainModelAdapter, self).__init__(*args, **kwargs)

    @staticmethod
    def cell_positions(cell_group_df):
        """Convert a data frame obtained as a result to a cell query
        to a generator of indexed cell position vectors.

        Parameters
        ------------------------------------------------------------------------
        cell_group_df :: pandas.DataFrame#result of a bluepy.v2 cell query
        ------------------------------------------------------------------------

        Result
        ------------------------------------------------------------------------
        a generator
        """
        return ([ro[0], np.array([ro[1][Cell.X], ro[1][Cell.Y], ro[1][Cell.Z]])]
                for ro in cell_group_df.iterrows())

