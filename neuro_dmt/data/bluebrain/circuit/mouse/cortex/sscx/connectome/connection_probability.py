"""Mouse SSCx circuit connectome data used for building and validating circuits
at the Blue Brain Project."""

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
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.connectome\
    import MouseSSCxConnectomeData

data_path_rat=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/rat/connectome",
        "connection_probability")
 
data_path_mouse=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/mouse/connectome",
        "connection_probability")

class MouseSSCxConnectionProbability(
        MouseSSCxConnectomeData):
    """Connection probability data for the mouse SSCx to be used for
     validations. We will include some rat data."""

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        reference_datasets=\
            self.get_reference_datasets()
        super().__init__(
            phenomenon = Phenomenon(
                "Connection Probability",
                "Probability that two cells (in a pathway) are connected.",
                group="connectome"),
            data_location=self.get_data_location(),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            measurement_parameters=["pre_mtype", "post_mtype"],
            *args, **kwargs)

    def get_data_location(self,
            reference_data_dir=None):
        """..."""
        return\
            {"lefort2009": os.path.join(
                "/gpfs/bbp.cscs.ch/home/sood",
                "work/validations/dmt",
                "neuro_dmt/data/bluebrain/circuit",
                "mouse/cortex/sscx/connectome",
                "connectome_probability.py")}

    def get_reference_datasets(self,
            reference_data_dir=None):
        """..."""

        dataframe=\
            pd.DataFrame(
                {"mean": [0.093, 0.093, 0.187, 0.187, 0.243,
                          0.072, 0.072, 0.19 , 0.028,  0.028],
                 "std":  10 * [np.nan]},
                index=pd.MultiIndex.from_tuples(
                    tuples=[
                        ("L2_TPC:A", "L2_TPC:A"),
                        ("L2_TPC:B", "L2_TPC:B"),
                        ("L3_TPC:A", "L3_TPC:A"),
                        ("L3_TPC:B", "L3_TPC:B"),
                        ("L4_UPC", "L4_UPC"),
                        ("L5_TPC:A", "L5_TPC:A"),
                        ("L5_TPC:B", "L5_TPC:B"),
                        ("L5_TPC:C", "L5_TPC:C"),
                        ("L6_TPC:A", "L6_TPC:A"),
                        ("L6_TPC:C", "L6_TPC:C")],
                    names=["pre_mtype", "post_mtype"]))

        lefort2009=\
            "lefort2009"
        return Record(
            primary=lefort2009,
            datasets={
                lefort2009: ReferenceData(
                    data=Record(
                        label=lefort2009,
                        uri=self.get_data_location()[lefort2009],
                        citation="Lefort 2009",
                        what="Connection probability of cell pairs \
                        in mtype-->mtype pathways.",
                        data=dataframe),
                    description="Ask SR",
                    measurement_parameters=["pre_mtype", "post_mtype"])})
