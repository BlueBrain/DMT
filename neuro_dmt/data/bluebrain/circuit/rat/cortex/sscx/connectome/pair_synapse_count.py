"""Rat SSCx circuit connectome data used for building and validation circuits 
at the Blue Brain Project"""

import os
import pickle
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.data\
    import ReferenceData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome\
    import RatSSCxConnectomeData

data_path=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/rat/connectome",
        "pair_synapse_count")

class RatSSCxPairSynapseCountData(
        RatSSCxConnectomeData):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        reference_datasets=\
            self.get_reference_datasets(
                data_path)
        super().__init__(
            phenomenon = Phenomenon(
                "Pair Synapse Count",
                "Count of synapses between a pair of cells.",
                group="connectome"),
            data_location=self.get_data_location(data_path),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            *args, **kwargs)

    def get_data_location(self,
            reference_data_dir):
        """..."""
        return\
            {"michael_reimann_2017": os.path.join(
                reference_data_dir,
                "2017-11-17_nsyn_SS_with_v6_mtypes.pickle")}

    def get_reference_datasets(self,
            reference_data_dir):
        """Available reference data to be used to validate cell density"""
        data_2017_path=\
            os.path.join(
                reference_data_dir,
                "2017-11-17_nsyn_SS_with_v6_mtypes.pickle")
        with open(data_2017_path, "rb") as file_2017:
            data_raw, data_read = pickle.load(file_2017)

        for k, v in data_raw.items():
            data_read[k] = (np.mean(v), np.std(v), len(v))

        data_read_list=\
            [(k, v) for k, v in data_read.items()]
        dataframe=\
            pd.DataFrame(
                [{"mean": value[0], "std": value[1], "sample_size": value[2]}
                  for _, value in data_read_list],
                index = pd.MultiIndex.from_tuples(
                    [key for key, _ in data_read_list],
                    names=("pre_mtype", "post_mtype")))
        mr2017=\
            "michael_reimann_2017"
        return Record(
            primary=mr2017,
            datasets={
                mr2017: ReferenceData(
                    data=Record(
                        label = mr2017,
                        uri = data_2017_path,
                        citation = "Curated by Michael Reimann, BBP, EPFL",
                        what = "Ask Michael Reimann",
                        data = dataframe),
                    description="Ask Michael Reimann")})
            
