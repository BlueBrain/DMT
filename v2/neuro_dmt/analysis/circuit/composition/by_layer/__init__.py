"""
Circuit composition analyses.
"""

import pandas
from .. import CompositionAnalysis
from ..interfaces import CellDensityAdapterInterface


class ByLayerCellDensityAnalysis(
        CompositionAnalysis):
    """
    Analysis of cell density by layer.
    """

    measurement_parameters =\
        pandas.Index( [1,2,3,4,5,6], name="layer" )

    AdapterInterface =\
        CellDensityAdapterInterface


    def get_measurement(self,
            *arg, **kwargs):
        """
        This sticks in the method to measure the circuit_model
        """
        return self.adapter.get_cell_density( *args, **kwargs)
