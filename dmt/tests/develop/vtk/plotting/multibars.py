"""Test develop multiple bar plots."""


import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.plotting\
    import BarPlot\
    ,      LinePlot
from dmt.vtk.plotting.bars\
    import MultiBarPlot
from dmt.vtk.measurement\
    import summary_statistic

N = 10
multi_dataframe=\
    pd.DataFrame(
        np.vstack([
            np.random.uniform(0., 1., N),
            np.random.uniform(0., 0.1, N),
            np.random.uniform(1., 10, N),
            np.random.uniform(0., 0.001, N)
        ]).transpose(),
        columns=pd.MultiIndex.from_tuples(
            tuples=[("T1", "mean"), ("T1", "std"),
                    ("T2", "mean"), ("T2", "std")]),
        index=pd.MultiIndex.from_tuples(
            tuples=[("first{}".format(f), "Second{}".format(s))
                     for f in range(1,6)
                     for s in range(1,3)],
            names=["first", "second"]))
multi_bar_plotter=\
    MultiBarPlot(
        Record(
            phenomenon=Phenomenon(
                "Test phenomenon",
                description="To test bar plot."),
            data=multi_dataframe,
            label="test-bar-plot"))
multi_bar_plotter\
    .plotting(
        "Y")\
    .versus(
        "first")\
    .given(
        second="Second2")\
    .with_customization(
        title="Title")

multi_bar_plotter.save(
    multi_bar_plotter.plot(),
    file_name="test_multi_bar_plot.png")

