import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.plotting\
    import HeatMap

dataframe = pd.DataFrame(
    dict(
        mean=[0.1, 0.3, 0.4, 0.5, 0.6, 0.7],
        std=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01]),
    index=pd.MultiIndex.from_tuples(
        tuples=[
            ("L23_MC", "L5_TPC:A"),
            ("L23_MC", "L5_TPC:B"),
            ("L23_MC", "L4_MC"),
            ("L4_MC", "L5_TPC:A"),
            ("L4_MC", "L5_TPC:B"),
            ("L5_TPC:B", "L23_MC")],
        names=["pre_mtype", "post_mtype"]))
heatmap = HeatMap(
    Record(
        data=dataframe,
        label="heatmap"),
    analyzed_quantity="mean")
    
heatmap.save(
    heatmap.plot(
        with_customization={
            "xvar": "post_mtype",
            "yvar": "pre_mtype"}),
    file_name="test_heatmap.png")
