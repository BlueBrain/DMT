"""Regression tests for dmt.vtk.plotting"""
import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting\
    import BarPlot\
    ,      LinePlot\
    ,      HeatMap
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
plot_figure=\
    test_bar_plot.plot()
test_bar_plot.save(
    plot_figure,
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
line_plot_figure=\
    test_line_plot.plot()
test_line_plot.save(
    line_plot_figure,
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
            "test_multi_dataframe_plot"))
line_plotter.save(
    line_plotter.plot(),
    file_name="test_multi_dataframe.png")

mean_std=\
    np.vstack([
        np.random.uniform(
            0, 1, 9),
        np.random.uniform(
            0, 0.1, 9),
        np.random.uniform(
            0, 1, 9),
        np.random.uniform(
            0, 0.01, 9)])\
      .transpose()
assert\
    mean_std.shape == (9,4)
heatmap_dataframe=\
    pd.DataFrame(
        mean_std,
        columns=pd.MultiIndex.from_tuples(
            [("X", "mean"), ("X", "std"), ("Y", "mean"), ("Y", "std")]),
        index=pd.MultiIndex.from_tuples(
            [(pre, post) for pre in ["one", "two", "three"]
             for post in ("one", "two", "three")],
            names=("pre", "post") ))
heatmap=\
    HeatMap(
        Record(
            data=heatmap_dataframe,
            label="heatmap"),
        analyzed_quantity="X")
heatmap.save(
    heatmap.plot(),
    file_name="test_heatmap.png")


mean_std_bad=\
    np.vstack([
        np.random.uniform(
            0, 1, 8),
        np.random.uniform(
            0, 0.1, 8),
        np.random.uniform(
            0, 1, 8),
        np.random.uniform(
            0, 0.01, 8)])\
      .transpose()
heatmap_dataframe_bad=\
   pd.DataFrame(
        mean_std_bad,
        columns=pd.MultiIndex.from_tuples(
            [("X", "mean"), ("X", "std"), ("Y", "mean"), ("Y", "std")]),
       index=pd.MultiIndex.from_tuples(
           [("one", "one"), ("two", "one"), ("three", "one"),
            ("one", "two"), ("two", "two"), ("three", "two"),
            ("one", "three"), ("two", "three")],
            names=("pre", "post") ))
heatmap_bad=\
    HeatMap(
        Record(
            data=heatmap_dataframe_bad,
            label="heatmap"),
        analyzed_quantity="Y")
heatmap_bad.save(
    heatmap_bad.plot(),
    file_name="test_heatmap_bad.png")
