"""Test develop Comparison BarPlot"""

import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting.comparison.barplot\
    import BarPlotComparison
from dmt.vtk.measurement\
    import summary_statistic

N = 20
    
layers=\
    range(1, 7)
datasets=\
    [0, 1]
regions=\
    range(1, 4)
    
def get_value(d, l):
    return np.random.normal(l, d) #mean of l and sigma of d

reference_data=\
    pd.DataFrame(
        {"mean": [get_value(d, l) for d in datasets for l in layers],
         "std":  [d for d in datasets for _ in layers]},
        index = pd.MultiIndex.from_tuples(
            tuples = [
                ("Dataset{}".format(d), "L{}".format(l))
                for d in datasets for l in layers],
            names = [
                "dataset", "layer"]))
measurement_data=\
    pd.DataFrame(
        {"mean": [get_value(0.5, r) for r in regions for l in layers],
         "std":  [r for r in regions for _ in layers]},
        index = pd.MultiIndex.from_tuples(
            tuples = [
                ("R{}".format(r), "L{}".format(l))
                for r in regions for l in layers],
            names = [
                "region", "layer"]))
            

bar_plot=\
    BarPlotComparison(
        Record(
            data=measurement_data,
            label="model"),
    ).against(
        reference_data
    ).plotting(
        "cell_density"
    ).versus(
        "layer"
    ).given(
        region="R2"
    ).with_customization(
        title = "Test Bar Plot")
# bar_plot=\
#     BarPlotComparison(
#         Record(
#             data=measurement_data,
#             label="model"),
#     ).against(
#         reference_data
#     ).comparing(
#         "dataset"
#     ).for_given(
#         "layer"
#     ).with_customization(
#         title = "Test Bar Plot")

def test_plot():
    bar_plot.save(
        bar_plot.plot(),
        output_dir_path = os.path.join(
            os.getcwd(),
            "test_comparison_plots"),
        file_name = "test_barplot.png")
