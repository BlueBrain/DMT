"""
Circuit composition analyses.
"""

import pandas
from .. import CompositionAnalysis, CellDensityAnalysis


class ByLayerCellDensityAnalysis(
        CompositionAnalysis,
        CellDensityAnalysis):
    """
    Analysis of cell density by layer.
    """

    measurement_parameters =\
        pandas.Index( [1,2,3,4,5,6], name="layer" )

    def plot(self)


