"""Test develop bar plots, for single analysis (not comparison)"""

import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting.bars\
    import BarPlot
from dmt.vtk.measurement\
    import summary_statistic

dataframe=\
    pd.DataFrame(
        dict(
            mean=[0.1, 0.2, 0.3, 0.4],
            std=[0.01, 0.01, 0.02, 0.01]))
test_bar_plot=\
    BarPlot(
        Record(
            data=dataframe,
            label="test"),
        title="Test Plot",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_analysis_bar_plot"))
plot_figure=\
    test_bar_plot.plot()
test_bar_plot.save(
    plot_figure,
    file_name="test_plot.png")

samples=\
    pd.DataFrame({
        "test": np.random.randint(0, 100, 100)})
samples.index=\
    pd.Index(
        ["T{}".format(i)
         for i in range(10)
         for _ in range(10)],
        name="Test")
summary_bar_plot=\
    BarPlot(
        Record(
            data=summary_statistic(samples),
            label="test"),
        title="Test Summary Statistics Plot",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_summary_statistics_plot"))
summary_bar_plot.save(
    summary_bar_plot.plot(),
    file_name="test_summary_statistics_plot.png")
