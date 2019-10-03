"""
Test (and develop) measurement tools.
"""
import pandas as pd
import numpy as np
import pytest as pyt
from .. import measurement
from ..measurement import Measurement, SampleMeasurement, SummaryMeasurement
from neuro_dmt.data import rat


def test_loading():
    """
    Measurement should be able to the right type of measurement.
    """
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
    
    with pyt.raises(TypeError):
        SampleMeasurement.load(by_layer_summary)
        
        summary_measurement =\
            Measurement.load(by_layer_summary)
        assert isinstance(summary_measurement, SummaryMeasurement)
        

def test_sampling():
    """
    Measurement should be able to produce a samples dataframe.
    """

    samples = rat.defelipe2017.samples(100)
    assert isinstance(samples, pd.DataFrame)
    assert samples.shape[0] == 600, "samples shape is {}".format(samples.shape)
    assert len(samples.columns) == 1

    samples = rat.meyer2010.samples(100)
    assert isinstance(samples, pd.DataFrame)
    assert samples.shape[0] == 600, "samples shape is {}".format(samples.shape)
    assert len(samples.columns) == 1

    samples =\
        measurement.get_samples(
            rat.defelipe2017.data[["layer", "cell_density"]].set_index("layer"))
    assert isinstance(samples, pd.DataFrame)
    assert samples.shape[0] == rat.defelipe2017.data.shape[0],\
        "samples shape is {}".format(samples.shape)
    assert len(samples.columns) == 1

    by_layer_samples =\
        pd.DataFrame(dict(
            layer=10 * list(range(1,7)),
            cell_density=np.random.uniform(low=0., high=1.e5, size=60)))\
          .set_index("layer")
    samples = measurement.get_samples(by_layer_samples, 100)
    assert isinstance(samples, pd.DataFrame)
    assert samples.shape[0] == 60, "samples shape is {}".format(samples.shape)
    assert len(samples.columns) == 1, "samples columns {}".format(samples.columns)

    summary = measurement.get_summary(by_layer_samples)
    assert isinstance(summary, pd.DataFrame)
    assert summary.shape[0] == 6, "summary shape is {}".format(summary.shape)
    assert isinstance(summary.columns, pd.MultiIndex)
    assert len(summary.columns) >= 2,\
        "summary columns {}".format(summary.columns)
    assert ("cell_density", "mean") in summary.columns,\
        "summary columns {}".format(summary.columns)
    assert ("cell_density", "std") in summary.columns,\
        "summary columns {}".format(summary.columns)

    by_layer_summary =\
        pd.DataFrame(
            {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
             ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
            index=pd.Index(range(1,7), name="layer"))

    samples = measurement.get_samples(by_layer_summary, 100)
    assert isinstance(samples, pd.DataFrame)
    assert samples.shape[0] == 600, "samples shape is {}".format(samples.shape)
    assert len(samples.columns) == 1

    summary = measurement.get_summary(by_layer_summary)
    assert isinstance(summary, pd.DataFrame)
    assert summary.shape[0] == 6, "summary shape is {}".format(summary.shape)
    assert isinstance(summary.columns, pd.MultiIndex),\
        "summary columns {}".format(summary.columns)
    assert len(summary.columns) >= 2,\
        "summary columns {}".format(summary.columns)
    assert ("cell_density", "mean") in summary.columns,\
        "summary columns {}".format(summary.columns)
    assert ("cell_density", "std") in summary.columns,\
        "summary columns {}".format(summary.columns)


    concatenated_summary =\
        measurement.concat_as_summaries({
            "one": by_layer_samples,
            "two": by_layer_summary})
