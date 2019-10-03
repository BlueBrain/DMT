"""
Test data manipulation done by `Plotters`.
"""

import pandas as pd
import numpy as np
from .. import get_dataframe


def test_get_dataframe():
    """
    `get_dataframe()` should return a dataframe from a dict or a dataframe
    """
by_layer_summary_1 =\
    pd.DataFrame(
        {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
         ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
        index=pd.Index(range(1,7), name="layer"))
by_layer_summary_2 =\
    pd.DataFrame(
        {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
         ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
        index=pd.Index(range(1,7), name="layer"))
 
samples =\
    get_dataframe({
        "one": by_layer_summary_1,
        "two": by_layer_summary_2})

assert isinstance(samples, pd.DataFrame)
assert "dataset" in samples.columns,\
    "samples dataframe {}".format(samples)
assert "one" in samples.dataset.values,\
    "samples dataframe {}".format(samples)
index = samples.index.names
assert len(index) == 1, "{}".format(index)
assert None in index, "{}".format(index)
