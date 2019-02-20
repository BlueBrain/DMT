"""Test and develop comparison plots.
We intend to use pandas Multiindex. Here we prototype our solution.
"""
import os
import pandas as pd
import numpy as np
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.circuit.composition.cortex.sscx.by_layer.cell_density \
    import get_reference_datasets

class Test:
    """..."""
    def __init__(self, test_env, *args, **kwargs):
        """...Run Me...
        
        Parameters
        ----------------------------------------------------------------------------
        test_env :: TestEnv."""
        self._test_env = test_env

        reference_data_path =  os.path.join(self._test_env.DMTDATASETSPATH,
                                            "cortex/sscx/rat",
                                            "cell_density")
        datasets = get_reference_datasets(reference_data_path)
        Nds = len(datasets.data)
        
        
        dataset_names = [k for k in datasets.data.keys()]
        self.reference_data \
            = pd.concat([datasets.data[name].data for name in dataset_names])\
                .set_index(
                    pd.MultiIndex.from_tuples([
                        (name, layer)
                        for name in dataset_names
                        for layer in sorted(datasets.data[name].data.region)
                    ],
                    names=("dataset", "region"))
                )[["mean", "std"]]

        self.model_data = Record(
            data = pd.DataFrame(dict(
                mean=100. * np.random.random(6),
                std=10 * np.random.random(6)
            )).set_index(pd.Int64Index(range(1, 7), name="region")),
            label = "in-silico"
        )


    def run(self):
        barp = BarPlotComparison(self.model_data)
        print("barp data", barp._data)
        return barp.comparing("dataset")\
                .against(self.reference_data)\
                .for_given("region")
