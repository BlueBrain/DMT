"""Test develop bar plots, for single analysis (not comparison)"""

import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting.bars\
    import BarPlot
from dmt.vtk.plotting.lines\
    import LinePlot
from dmt.vtk.measurement\
    import summary_statistic

dataframe=\
    pd.DataFrame(
        dict(
            mean=[0.1, 0.2, 0.3, 0.4],
            std=[0.01, 0.01, 0.02, 0.01]),
        index=pd.Index(
            ["L{}".format(i) for i in range(4)]))
test_bar_plot=\
    BarPlot(
        Record(
            data=dataframe,
            label="test"),
        title="Test Plot",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_analysis_bar_plot"))

def make_bar_plot():
    test_bar_plot.save(
        test_bar_plot.plot(),
        file_name="test_bar_plot.png")

test_line_plot=\
    LinePlot(
        Record(
            data=dataframe,
            label="test"),
        title="Test Plot",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_analysis_line_plot"))

def make_simple_line_plot():
    return\
        test_line_plot.save(
            test_line_plot.plot(),
            file_name="test_line_plot.png")

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
def make_summary_bar_plot():
    return\
        summary_bar_plot.save(
            summary_bar_plot.plot(),
            file_name="test_summary_statistics_plot.png")

multi_dataframe=\
    pd.DataFrame(
    {"mean": np.random.uniform(0, 1, 99),
     "std":  np.random.uniform(0, 0.1, 99)},
     index = pd.MultiIndex.from_tuples(
         tuples=[(depth, subregion, region)
                 for region in ["SSp"]
                 for subregion in ["SSp-ll", "SSp-fl", "SSp-m"]
                 for depth in np.linspace(0, 1, 33)],
         names=("depth", "subregion", "region")))

line_plotter=\
    LinePlot(
        Record(
            data=multi_dataframe,
            label="random_numbers")
    ).plotting(
        "density"
    ).versus(
        "depth"
    ).given(
        region="SSp",
        subregion="SSp-ll"
    ).with_customization(
        title="Test plot MultiIndexed DataFrame",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_multi_dataframe_plot"),
        axis={
            "xmin": 0.,
            "xmax": 1.,
            "ymin": np.min(multi_dataframe["mean"].values),
            "ymax": np.max(multi_dataframe["mean"].values)})

def make_line_plot():
    return\
        line_plotter.save(
            line_plotter.plot(),
            file_name="test_multi_dataframe.png")

dataframe_onepoint=\
    pd.DataFrame(
        dict(
            mean=[0.1],
            std=[0.01],
        index=pd.Index(
            ["L{}".format(i) for i in range(1,2)])))
test_line_plot_one=\
    LinePlot(
        Record(
            data=dataframe_onepoint,
            label="test"),
        title="Test Plot",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_analysis_one_line_plot"))
def make_one_point_line_plot():
    return\
        test_line_plot_one.save(
            test_line_plot_one.plot(),
            file_name="line_plot_with_1_point.png")
