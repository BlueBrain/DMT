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
from dmt.model import Callable, AIBase
from dmt.data import ReferenceData
from dmt.vtk.utils.collections import Record
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
    reference_data = Field.Optional(
        __name__="reference_data",
        __type__=ReferenceData,
        __doc__="If not provided, assume validation does not use reference data")

    p_value_threshold = Field(
        __name__="p_value_threshold",
        __type__=float,
        __is_valid__=lambda instance, value: value > 0,
        __default__=0.05,
        __doc__="p-value threshold to determine if a validation passed or not.")

    plotter_type = Field.Optional(
        __name__="plotter_type",
        __typecheck__=Field.typecheck.subtype(ComparisonPlot),
        __doc__="""A subclass of {} to be used plot the results of
        this validation.""".format(ComparisonPlot))

    plot_customization = Field.Optional(
        __name__="plot_customizaion",
        __type__=dict,
        __doc__="A dict containing customization of the plot.")

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


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
            raise Exception("Validation test case {} does not use reference data"\
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

        dataset_names = [k for k in data.keys()]

        fdf = flatten({n: data[n].data for n in dataset_names},
                      names=["dataset"])[["mean", "std"]]

        return fdf.set_index(
            pd.MultiIndex(levels=fdf.index.levels, labels=fdf.index.labels,
                          names=[n.lower() for n in fdf.index.names]))

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


    def get_validation_data(self):
        """..."""
        try:
            return self.reference_data.data
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_data(),
                "Could not get data from reference data.",
                "\t AttributeError: {}".format(e))

        return None

    def get_verdict(self, p):
        """Use p-value threshold to judge if the validation was a success.
        The user may override this method in their concrete implementation.

        Parameters
        ------------------------------------------------------------------------
        p :: Float #p-value of an experimental measurement.
        """
        if np.isnan(p):
            return Verdict.NA
        if p > self.p_value_threshold:
            return Verdict.PASS
        if p<= self.p_value_threshold:
            return Verdict.FAIL
        return Verdict.INCONCLUSIVE

    def pvalue_table(self, model_measurement):
        """p-value table of a model_measurement that may be a scalar, that is a 
        data-frame with a single row, or a vector, represented as a data-frame
        with more than one row.

        Default implementation, Override for your model_measurement

        Parameters
        ------------------------------------------------------------------------
        model_mesaurement :: Record(...)
        """
        from scipy.special import erf
        from numpy import abs, sqrt

        if model_measurement.label in model_measurement.data:
            model_data = model_measurement.data[model_measurement.label]
        else:
            model_data = model_measurement.data

        real_measurement = self.pvalue_dataset
        if real_measurement is not None:
            delta_mean\
                = abs(model_data["mean"] - real_measurement.data["mean"])
            stdev\
                = sqrt(model_data["std"]**2 + real_measurement.data["std"]**2)
            z_score = delta_mean / stdev
            pval = 1. - erf(z_score)
            return pd.DataFrame(dict(
                delta_mean = delta_mean,
                std = stdev,
                z_score = z_score,
                pvalue = pval))
        else:
            self.logger.alert(
                self.logger.get_source_info(),
                "no primary dataset set")
        return pd.DataFrame()

    def pvalue(self, model_measurement):
        """Scalar valued  p-value.
        If measurement is vector-valued, then a pooled value will be returned.
        Default implementation, Override for your model_measurement
        """
        from dmt.vtk.statistics import FischersPooler
        N = model_measurement.data.shape[0]
        pvt = self.pvalue_table(model_measurement)

        if pvt.shape[0] > 0:
            if N == 1:
                return float(pvt.pvalue)
            else:
                return FischersPooler.eval(pvt.pvalue)
        return np.nan

    @property
    def primary_dataset(self):
        """..."""
        return self.reference_data.primary_dataset

    @property
    def pvalue_dataset(self):
        """..."""
        return self.reference_data.primary_dataset

@document_fields
class SinglePhenomenonValidation(
        ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion."""

    phenomenon = Field(
        __name__="phenomenon",
        __type__=Phenomenon,
        __doc__="""A SinglePhenomenonValidation can have only one Phenomenon
        that is measured, validated, and reported.""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        super().__init__(
            phenomenon=phenomenon,
            phenomena={phenomenon},
            analysis_type="validation",
            *args, **kwargs)

    def _get_output_dir(self):
        """..."""
        try:
            odp = self.output_dir_path
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "No 'output_dir_path'",
                "\tAttributeError: {}".format(e))
            odp = None

        animal_region_path = os.path.join(
            odp if odp else os.getcwd(),
            "validation",
            self.animal,
            self.brain_region.label)

        if not self.phenomenon.group:
            return os.path.join(
                animal_region_path,
                self.phenomenon.label)
        return os.path.join(
            animal_region_path,
            self.phenomenon.group,
            self.phenomenon.label)

    def plot(self, *args, **kwargs):
        """Not implemented by default,
        but not abstractmethod,
        either so that you can actually create an instance without
        overriding."""
        raise NotImplementedError()

    def get_caption(self, model_measurement):
        """Caption that will be shown below the validation plot.

        Implementation Notes
        ------------------------------------------------------------------------
        Measurement method must be known to produce an informative caption.
        However this information is available only to the model adapter, and
        not to the class representing the validation itself. The author of the
        concrete implementation of SinglePhenomenonValidation will have to
        determine where to get the information required to produce a caption.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(phenomenon :: Phenomenon#that was measured,
        ~                           label :: String,#used to label the measureemnt
        ~                           region_label :: String,#for regions measured
        ~                           data :: DataFrame["region", "mean", "std"],
        ~                           method :: String #how measurement was made.])
        """
        return "{} is plotted. {}\n Method: {}"\
            .format(self.phenomenon.title,
                    self.phenomenon.description,
                    model_measurement.method)

