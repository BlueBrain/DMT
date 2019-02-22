"""Rat SSCx circuit connectome data used for building and validation circuits 
at the Blue Brain Project"""

import os
import pickle
import numpy as np
from scipy import stats
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
        "connection_probability")

class RatSSCxConnectionProbability(
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
                "Connection Probability",
                "Probability that two cells (in a pathway) are connected.",
                group="connectome"),
            data_location=self.get_data_location(data_path),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            measurement_parameters=["pre_mtype", "post_mtype"],
            *args, **kwargs)


    def get_data_location(self,
            reference_data_dir):
        """..."""
        return\
            {"michael_reimann_2017": os.path.join(
                reference_data_dir,
                "con_probs_SS_2017_11_23.pickle")}

    def get_reference_datasets(self,
            reference_data_dir):
        """..."""
        data_file_path=\
            os.path.join(
                reference_data_dir,
                "con_probs_SS_2017_11_23.pickle")
        with open(data_file_path, "rb") as data_file:
            data_raw= pickle.load(data_file)
        data_raw_list=\
            list(data_raw.items())

        def __get_connection_row(
                connection_data):
            """..."""
            probability_mean=\
                connection_data[0]
            sample_size=\
                connection_data[2]
            binom_std=\
                np.sqrt(
                    stats.binom.stats(
                        sample_size,
                        probability_mean)[1])
            probability_std=\
                binom_std/sample_size
            return\
                pd.Series({
                    "mean": probability_mean,
                    "std":  probability_std,
                    "sample_size": sample_size})

        dataframe=\
            pd.DataFrame(
                [__get_connection_row(connection_data)
                 for _, connection_data in data_raw_list],
                index = pd.MultiIndex.from_tuples(
                    [pre_post_mtypes for pre_post_mtypes, _ in data_raw_list],
                    names=("pre_mtype", "post_mtype")))
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
                            what="Connection probability between \
                            mtype-->mtype pathways.",
                            data=dataframe),
                        description="Ask Michael Reimann",
                        measurement_parameters=["pre_mtype", "post_mtype"])})
