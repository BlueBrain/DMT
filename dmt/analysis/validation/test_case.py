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
from dmt.analysis.comparison import Comparison
#from dmt.analysis import Analysis
from dmt.vtk.utils.pandas import flatten
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class ValidationTestCase(
        Comparison):
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adaptermethod', and use them like any other method.
    """
    reference_data=\
        Field.Optional(
            __name__="reference_data",
            __type__=ReferenceData,
            __doc__="""If not provided, assume validation does not use
            reference data""")
    plotter_type=\
        Field.Optional(
            __name__="plotter_type",
            __typecheck__=Field.typecheck.subtype(ComparisonPlot),
            __doc__="""A subclass of {} to be used plot the results of
            this validation.""".format(ComparisonPlot))
    plot_customization=\
        Field.Optional(
            __name__="plot_customizaion",
            __type__=dict,
            __doc__="A dict containing customization of the plot.")

    def __init__(self,
            *args, **kwargs):
        """..."""
        self.analysis_type=\
            "validation"
        super().__init__(
            *args, **kwargs)

    @property
    def _reference_data(self):
        """..."""
        try:
            return self.reference_data.data
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "Caught Attribute Error: \n\t{}".format(e))

        return None

    @property
    def validation_data(self):
        """Override"""
        if not hasattr(self, "reference_data"):
            raise Exception(
                "Validation test case {} does not use reference data"\
                .format(self.__class__.__name__))
        data = self._reference_data
        if not data:
            return data

        if not isinstance(data, dict):
            if not isinstance(data, pd.DataFrame):
                raise AttributeError(
                    "Reference data is not a pandas DataFrame, but {}\n{}"\
                    .format(type(data).__name__, data))
            return data

        assert(isinstance(data, dict))

        dataset_names=\
            [k for k in data.keys()]
        flattened_dataframe=\
            flatten({
                n: data[n].data for n in dataset_names},
                names=["dataset"]
            )[["mean", "std"]]
        return\
            flattened_dataframe.set_index(
                pd.MultiIndex(
                    levels=flattened_dataframe.index.levels,
                    labels=fdf.index.labels,
                    names=[n.lower() for n in flattened_dataframe.index.names]))
                       
    @property
    def reference_datasets(self):
        """Return validation data as a dict."""
        data = self._reference_data
        if not data:
            return None
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {d.label: d for d in data}
        return {data.label: data}

    @property
    def validation_datasets(self):
        """another name for reference_datasets"""
        return self.reference_datasets

    def data_description(self):
        """Describe the experimental data used for validation."""
        return self.reference_data.description

    def get_reference_data(self):
        """..."""
        try:
            return self.reference_data.data
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_data(),
                "Could not get data from reference data.",
                "\t AttributeError: {}".format(e))

        return None

    @property
    def primary_dataset(self):
        """..."""
        return self.reference_data.primary_dataset

    @property
    def get_dataset_for_pvalue_calculation(self):
        """..."""
        return self.reference_data.primary_dataset

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

