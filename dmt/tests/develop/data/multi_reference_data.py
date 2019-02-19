"""Test develop MultiReferenceData"""

import numpy as np
import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.data.reference\
    import ReferenceData\
    ,      MultiReferenceData
from dmt.vtk.phenomenon\
    import Phenomenon


N = 6
index=\
    pd.Index(
    ["L{}".format(l) for l in range(1, 7)])
dataset_one=\
    Record(
        label="deeone",
        data=pd.DataFrame(
            {"mean": np.random.uniform(0., 1., N),
             "std": np.random.uniform(0.0, 0.01, N)},
            index=index))
dataset_two=\
    Record(
        label="deetwo",
        data=pd.DataFrame(
            {"mean": np.random.uniform(1., 2., N),
             "std": np.random.uniform(0., 0.01, N)},
            index=index))
multi_data=\
    MultiReferenceData(
        phenomenon=Phenomenon(
            "Test",
            "Test test",
            group="Test"),
        data_location={
            dataset_one.label: "",
            dataset_two.label: ""},
        datasets={
            dataset_one.label: ReferenceData(
                data=dataset_one,
                description="test dataset one"),
            dataset_two.label: ReferenceData(
                data=dataset_two,
                description="test dataset two")},
        primary=dataset_one.label)

dataset_three=\
    Record(
        label="deethree",
        data=pd.DataFrame(
            {"mean": np.random.uniform(2., 3., N),
             "std": np.random.uniform(0., 0.01, N)},
            index=index))



