"""Multi-indexed DataFrame is very useful."""
import pandas as pd
import numpy as np
from dmt.vtk.utils.collections import Record

mtypes = set(["MC", "ChC", "PC", "TPC"])
layers = range(1, 7)

def create_datasets(name):
    """Create a dataset with given name, and a multi-index."""
    mtype_mean = {"MC": 1.e0, "ChC": 1.e-1, "PC": 1.e2, "TPC": 1.e1}
    layer_mean = {1: 1.e0, 2: 1.e1, 3: 1.e2, 4: 1.e1, 5: 1.e2, 6: 1.e1}
    def mean(layer, mtype):
        """random mean"""
        return mtype_mean[mtype] * layer_mean[layer] * np.random.random()
    def std(layer, mtype):
        """random mean"""
        return np.sqrt(mtype_mean[mtype] * layer_mean[layer]) * np.random.random()
        
    dataframe = pd.DataFrame({"Layer": layer,
                              "Mtype": mtype,
                              "mean": mean(layer, mtype),
                              "std": std(layer, mtype)}
                             for layer in layers for mtype in mtypes)\
                  .set_index(["Layer", "Mtype"])
    
    return Record(data=dataframe, label=name)



datasets = {"XYZ 1011": create_datasets("xyz1011"),
            "XYZ 2011": create_datasets("xyz2011"),
            "ABC 505": create_datasets("abc505")}


def flatten(dataframes, keys=None, names=None):
    """Flatten a collection of dataframes."""
    if isinstance(dataframes, dict):
        keys = list(dataframes.keys())
        return flatten([dataframes[k] for k in keys], keys=keys, names=names)

    return pd.concat(dataframes, keys=keys, names=names)
