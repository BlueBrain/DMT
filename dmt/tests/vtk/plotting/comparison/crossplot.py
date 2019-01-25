"""Test develop Comparison CrossPlot."""

import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting.comparison.crossplot\
    import CrossPlotComparison
from dmt.vtk.measurement\
    import summary_statistic

N = 20
index=\
    pd.Index(
        ["T{}".format(i) for i in range(N)],
        name="type")
mindex=\
    pd.MultiIndex.from_tuples(
        tuples=[("RD0", i) for i in index],
        names=["dataset", index.name])
columns=\
    pd.MultiIndex.from_tuples(
        tuples=[("reference", "mean"), ("reference", "std")],
        names=["source", "measurement"])
reference_columns=\
    pd.MultiIndex.from_tuples(
        tuples=[("reference", "mean"), ("reference", "std")],
        names=["source", "measurement"])
reference_data=\
    pd.DataFrame(
        {"mean": np.linspace(0., 1., N),
         "std": 0.01 * np.ones(N)},
        index=index)
alternative_columns=\
    pd.MultiIndex.from_tuples(
        tuples=[("alternative", "mean"), ("alternative", "std")],
        names=["source", "measurement"])
alternative_data=\
    pd.DataFrame(
        np.array([
            np.linspace(0., 1., N) + np.random.uniform(0., 0.1, N),
            0.1 * np.ones(N)
        ]).transpose(),
        index=index,
        columns=alternative_columns)
test_cross_plot=\
     CrossPlotComparison(
         Record(
             data=alternative_data,
             label="alternative")
     ).against(
         reference_data
     ).with_customization(
         title="Test Cross Plot",
         output_dir_path=os.path.join(
             os.getcwd(),
             "test_comparison_plots"))
 
# test_cross_plot=\
#     CrossPlotComparison(
#         Record(
#             data=alternative_data,
#             label="alternative")
#     ).against(
#         reference_data
#     ).comparing(
#         "dataset"
#     ).for_given(
#         "type"
plot_figure=\
     test_cross_plot.plot(
         save=False)
test_cross_plot.save(
     plot_figure,
     file_name="test_plot.png")

