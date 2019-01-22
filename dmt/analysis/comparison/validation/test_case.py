""" Some base classes for validations.

Implementation Notes
--------------------------------------------------------------------------------
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of a validation class will accept a data object.
"""

from abc import abstractmethod
import os
import numpy as np
import pandas as pd
from dmt.analysis import OfSinglePhenomenon
from dmt.data import ReferenceData
from dmt.vtk.utils.collections import Record
#from dmt.analysis.comparison import Comparison
#from dmt.analysis import Analysis
from dmt.vtk.utils.pandas import flatten
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class ValidationTestCase:
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adaptermethod', and use them like any other method.
    """
    reference_data=\
        Field(
            __name__="reference_data",
            __type__=ReferenceData,
            __doc__="""A validation needs reference data to compare the
            model against.""")
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.analysis_type=\
            "validation"
        super().__init__(
            *args, **kwargs)

    @property
    def validation_data(self):
        """Override"""
        if not hasattr(self, "reference_data"):
            raise Exception(
                "Validation test case {} does not use reference data"\
                .format(self.__class__.__name__))

        data = self.reference_data.data

        self.logger.debug(
            self.logger.get_source_info(),
            "validation_data for reference data:\n {}".format(data))

        if not data:
            return pd.DataFrame()

        if isinstance(data, pd.DataFrame):
            return data

        if isinstance(data, dict):
            dataset_names=\
                list(data.keys())

            self.logger.debug(
                self.logger.get_source_info(),
                "dataset names: {}".format(dataset_names))

            flattened_dataframe=\
                flatten(
                    {n: data[n].data for n in dataset_names},
                    names=["dataset"]
                )[["mean", "std"]]
            return\
                flattened_dataframe.set_index(
                    pd.MultiIndex(
                        levels=flattened_dataframe.index.levels,
                        labels=flattened_dataframe.index.labels,
                        names=[name.lower()
                               for name in flattened_dataframe.index.names]))

        raise AttributeError(
            "Reference data is neither a 'dict', nor a pandas DataFrame",
            "It is a {}\n{}"\
            .format(type(data).__name__, data))

    @property
    def reference_datasets(self):
        """Return validation data as a dict."""
        data = self._reference_data
        if data is None:
            return None
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {d.label: d for d in data}
        if isinstance(data, pd.DataFrame):
            return {'dataset': data}
        return {data.label: data}

    @property
    def validation_datasets(self):
        """another name for reference_datasets"""
        return self.reference_datasets

    @property
    def primary_dataset(self):
        """..."""
        return self.reference_data.primary_dataset

    @property
    def reference_data_for_statistical_comparison(self):
        """..."""
        return self.reference_data.primary_dataset

    @property
    def reference_data_for_plotting(self):
        """..."""
        return self.validation_data

@document_fields
class SinglePhenomenonValidation(
        OfSinglePhenomenon,
        ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion."""

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        super().__init__(
            phenomenon,
            analysis_type="validation",
            *args, **kwargs)

    def plot(self, *args, **kwargs):
        """Not implemented by default,
        but not abstractmethod,
        either so that you can actually create an instance without
        overriding."""
        raise NotImplementedError()

