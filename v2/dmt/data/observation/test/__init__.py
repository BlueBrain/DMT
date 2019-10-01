"""
Test (and develop) measurement tools.
"""
import pandas as pd
import numpy as np
import pytest as pyt
from ..measurement import Measurement, SampleMeasurement, SummaryMeasurement


by_layer_samples =\
    pd.DataFrame(dict(
        layer=10 * list(range(1,7)),
        cell_density=np.random.uniform(low=0., high=1.e5, size=60)))\
      .set_index("layer")

with pyt.raises(TypeError):
    SummaryMeasurement.load(by_layer_samples)

sample_measurement =\
    SampleMeasurement.load(by_layer_samples)
assert isinstance(sample_measurement, SampleMeasurement)

sample_measurement =\
    Measurement.load(by_layer_samples)
assert isinstance(sample_measurement, SampleMeasurement)

by_layer_summary =\
    pd.DataFrame(
        {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
         ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
        index=pd.Index(range(1,7), name="layer"))
summary_measurement =\
    Measurement.load(by_layer_summary)

with pyt.raises(TypeError):
    SampleMeasurement.load(by_layer_summary)

assert isinstance(summary_measurement, SummaryMeasurement)

