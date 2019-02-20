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
        "inhibitory_synapses_on_soma")

class RatSSCxInhibitorySynapsesOnSomaData(
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
                "Inhibitory Synapses on Soma",
                "Count of inhibitory synapses on soma.",
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
                data_path,
                "inh_syns_on_soma.pickle")}

    def get_reference_datasets(self,
            reference_data_dir):
        """..."""
        data_file_location=\
            os.path.join(
                data_path,
                "inh_syns_on_soma.pickle")
        with open(data_file_location, "rb") as data_file:
            data_raw = pickle.load(data_file)

        data_read=[
            (k, (np.mean(v), np.std(v), len(v)))
            for k, v in data_raw.items()]
        dataframe=\
            pd.DataFrame(
                [{"mean": value[0],
                  "std": value[1],
                  "sample_size": value[2]}
                 for _, value in data_read],
                index=pd.Index(
                    [key for key, _ in data_read],
                    name="mtype"))
        mr2017=\
            "michael_reimann_2017"
        return\
            Record(
                primary=mr2017,
                datasets={
                    mr2017: ReferenceData(
                        data=Record(
                            label=mr2017,
                            uri=data_path,
                            citation="Curated by Michael Reimann, BBP, EPFL",
                            what="Ask Michael Reimann",
                            data=dataframe),
                        description="Ask Michael Reimann")})
