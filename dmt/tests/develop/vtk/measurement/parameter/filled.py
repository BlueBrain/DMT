"""Fill missing rows."""

import pandas as pd
from dmt.vtk.utils.logging\
    import Logger
from neuro_dmt.measurement.parameter\
    import CorticalLayer

log=\
    Logger(
        __file__,
        level=Logger.level.DEVELOP)
cortical_layer=\
    CorticalLayer()
dataframe_with_missing_value=\
    cortical_layer.filled(
        pd.DataFrame(
            {"mean": [1, 2, 3, 5, 6],
             "std":  [0.1, 0.1, 0.01, 0.1, 0.1]},
            index = pd.MultiIndex.from_tuples(
                tuples=[("MOp", i) for i in [1,2,3,5,6]],
                names=["region", "layer"])))
dataframe_without_missing_value=\
    cortical_layer.filled(
        pd.DataFrame(
            {"mean": [1, 2, 3, 4, 5, 6],
             "std":  [0.1, 0.1, 0.01, 0.01, 0.1, 0.1]},
            index = pd.MultiIndex.from_tuples(
                tuples=[("SSp-ll", i) for i in [1,2,3,4,5,6]],
                names=["region", "layer"])))
        
