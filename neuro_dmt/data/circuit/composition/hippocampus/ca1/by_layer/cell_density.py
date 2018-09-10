"""By layer cell density data."""
import numpy as np
import pandas as pd
import dmt.vtk.datasets as datasets

from dmt.vtk.utils.collections import Record

def get_reference_datasets(reference_data_dir):
    """Available reference data to be used to validate cell density."""
    armando = datasets.load(reference_data_dir, "Armando2017")
    armando.label = armando.short_name
    layers = ["SLM", "SR", "SP", "SO"]
    data = armando.data 
    armando.data = pd.DataFrame({
        "region": layers,
        "mean":  [1.e-3 * sum(data[l].values()) for l in layers],
        "std": len(layers) * [0.0]
    })
    return Record(
        datasets={armando.short_name: armando},
        primary=armando.short_name
    )
