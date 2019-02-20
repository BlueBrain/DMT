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
from dmt.vtk.measurement.parameter.finite\
    import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random\
    import ConditionedRandomVariate


N = 6
pre_mtype=\
    FiniteValuedParameter(
        label="pre_mtype",
        value_type=str,
        values=["L2_MC", "L1_TPC", "L23_MC", "L6_TPC"])
post_mtype=\
    FiniteValuedParameter(
        label="post_mtype",
        value_type=str,
        values=["L2_MC", "L1_TPC", "L23_MC", "L6_TPC"])
regions=\
    FiniteValuedParameter(
        label="region",
        value_type=str,
        values=["R1", "R2"])
index=\
    pd.Index(
        ["L{}".format(l) for l in range(1, 7)],
        name="layer")
l_dataset_one=\
    Record(
        label="deeone",
        data=pd.DataFrame(
            {"mean": np.random.uniform(0., 1., N),
             "std": np.random.uniform(0.0, 0.01, N)},
            index=index))
l_dataset_two=\
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
            l_dataset_one.label: "",
            l_dataset_two.label: ""},
        datasets={
            l_dataset_one.label: ReferenceData(
                data=l_dataset_one,
                description="test dataset one",
                measurement_parameters=["layer"]),
            l_dataset_two.label: ReferenceData(
                data=l_dataset_two,
                description="test dataset two",
                measurement_parameters=["layer"])},
        primary=l_dataset_one.label,
        measurement_parameters=["layer"])

dataset_three=\
    Record(
        label="deethree",
        data=pd.DataFrame(
            {"mean": np.random.uniform(2., 3., N),
             "std": np.random.uniform(0., 0.01, N)},
            index=index))

pathways_1=[
    ("L2_MC", "L23_TPC"),
    ("L2_MC", "L6_TPC"),
    ("L1_TPC", "L23_MC"),
    ("L6_TPC", "L1_TPC")]
m_index_1=\
    pd.MultiIndex.from_tuples(
        tuples=pathways_1,
        names=["pre_mtype", "post_mtype"])
m_dataset_1=\
    Record(
        label="deeone",
        data=pd.DataFrame(
            {"mean": np.random.uniform(0., 1., len(pathways_1)),
             "std": np.random.uniform(0., 0.01, len(pathways_1))},
             index=m_index_1))
pathways_2=[
    ("L2_MC", "L23_TPC"),
    ("L2_MC", "L4_TPC"),
    ("L4_TPC", "L23_MC"),
    ("L6_TPC", "L1_TPC")]
m_index_2=\
    pd.MultiIndex.from_tuples(
        tuples=pathways_2,
        names=["pre_mtype", "post_mtype"])
m_dataset_2=\
    Record(
        label="deetwo",
        data=pd.DataFrame(
            {"mean": np.random.uniform(0., 1., len(pathways_2)),
             "std": np.random.uniform(0., 0.01, len(pathways_2))},
             index=m_index_2))
pathway_data=\
    MultiReferenceData(
        phenomenon=Phenomenon(
            "Test Pathway Data",
            "Test"),
        data_location={
            m_dataset_1.label: "",
            m_dataset_2.label: ""},
        datasets={
            m_dataset_1.label: ReferenceData(
                data=m_dataset_1,
                description="",
                measurement_parameters=["pre_mtype", "post_mtype"]),
            m_dataset_2.label: ReferenceData(
                data=m_dataset_2,
                description="",
                measurement_parameters=["pre_mtype", "post_mtype"])},
        primary=m_dataset_1.label,
        measurement_parameters=["pre_mtype", "post_mtype"])


class TestRandomVariate(
        ConditionedRandomVariate):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            label="test_random_variate",
            value_type=int,
            reset_condition_type=True,
            columns=["R"],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        pre_mtype=\
            condition.get_value("pre_mtype")
        post_mtype=\
            condition.get_value("post_mtype")
        region=\
            condition.get_value("region")
        return\
            np.random.randint(10)\
            + len(pre_mtype)\
            + len(post_mtype)\
            + len(region)

    @property
    def sampling_method(self):
        """..."""
        return\
            """A random int 0 to 10 was added
            to the total length of pre and post mtype and region names."""


test_random_variate=\
    TestRandomVariate().given(
        pre_mtype,
        post_mtype,
        regions)
test_conditions=[
    condition.as_dict
    for condition in test_random_variate.conditions]
pathway_data_param_dicts=[
    dict(condition_tuple)
    for condition_tuple in pathway_data.measurement_parameters_values]

def is_permissible(condition):
    condition_dict=\
        condition.as_dict
    return any(
        all(
            condition_dict.get(
                param_label, None)\
            == param_value
            for param_label, param_value in data_param_pairs)
        for data_param_pairs in pathway_data.measurement_parameters_values)


accepted_df=\
    pd.DataFrame(
        [{"region": condition.get_value("region"),
          "pre_mtype": condition.get_value("pre_mtype"),
          "post_mtype": condition.get_value("post_mtype"),
          "accepted": pathway_data.contains(condition.as_dict)}
         for condition in test_random_variate.conditions])
