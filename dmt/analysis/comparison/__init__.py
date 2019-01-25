"Compare two models."
from abc import abstractmethod
import os
import numpy as np
import pandas as pd
from dmt.analysis import Analysis, OfSinglePhenomenon
from dmt.data import ReferenceData
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.utils.collections import Record
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class Comparison:
    """Compare an alternative against a reference."""

    p_value_threshold=\
        Field(
            __name__="p_value_threshold",
            __type__=float,
            __is_valid__=lambda instance, value: value > 0,
            __default__=0.05,
            __doc__="""p-value threshold to determine if a validation passed
            or not.""")
    reference_data=\
        Field.Optional(
            __name__="reference_data",
            __type__=ReferenceData,
            __doc__="""If not provided, assume comparison does not use
            reference data""")
    Plotter=\
        Field.Optional(
            __name__="Plotter",
            __typecheck__=Field.typecheck.subtype(ComparisonPlot),
            __doc__="""A subclass of {} to be plot comparison
            results.""".format(ComparisonPlot))
    plot_customization=\
        Field.Optional(
            __name__="plot_customization",
            __type__=dict,
            __doc__="A dict containing customization of the plot.")


    def __init__(self,
            *args, **kwargs):
        """..."""
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
                "Could not get data from reference data.",
                "Caught AttributeError: \n\t{}".format(e))
        return None

    def get_reference_data(self):
        """..."""
        return self._reference_data

    def data_description(self):
        """Describe the experimental data used for validation."""
        return self.reference_data.description

    @property
    @abstractmethod
    def reference_data_for_statistical_comparison(self):
        """..."""
        raise NotImplementedError(
            "Prepare the reference data for statistical comparison.")

    @property
    @abstractmethod
    def reference_data_for_plotting(self):
        """Prepare the dataset to be plotted."""
        raise NotImplementedError(
            "Prepare the reference data to plot.")

    def get_verdict(self, p_value):
        """Use p-value threshold to judge if the validation was a success.
        The user may override this method in their concrete implementation.

        Parameters
        ------------------------------------------------------------------------
        p :: Float #p-value of an experimental measurement.
        """
        if np.isnan(p_value):
            return Verdict.NA
        if p_value > self.p_value_threshold:
            return Verdict.PASS
        if p_value<= self.p_value_threshold:
            return Verdict.FAIL
        return Verdict.INCONCLUSIVE

    def pvalue_table(self,
            model_measurement):
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

        model_data=(
            model_measurement.data[model_measurement.label]
            if model_measurement.label in model_measurement.data 
            else model_measurement.data)
        reference_measurement=\
            self.reference_data_for_statistical_comparison
        if reference_measurement is not None:
            delta_mean=\
                abs(
                    model_data["mean"] - reference_measurement.data["mean"])
            stdev=\
                sqrt(
                    model_data["std"]**2 + reference_measurement.data["std"]**2)
            z_score=\
                delta_mean / stdev
            return pd.DataFrame(dict(
                delta_mean = delta_mean,
                std = stdev,
                z_score = z_score,
                pvalue = 1. - erf(z_score)))
        else:
            self.logger.alert(
                self.logger.get_source_info(),
                "no primary dataset set")
        return pd.DataFrame()

    def pvalue(self,
            model_measurement):
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



@document_fields
class ModelComparison(
        Comparison):
    """Compare an alternative model against a reference model.
    """
    reference_model=\
        Field(
            __name__="reference_model",
            __doc__="""Reference model against which alternative models can be
            compared.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args,
            reference_data=self.get_reference_measurement(*args, **kwargs),
            **kwargs)

    @property
    def reference_data_for_statistical_comparison(self):
        """..."""
        return self.reference_data


class SinglePhenomenonModelComparison(
        OfSinglePhenomenon,
        ModelComparison):
    """Compare a single phenomenon's measurement of an alternative model
    against that of a reference model."""

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            analysis_type="model-comparison",
            *args, **kwargs)

    def plot(self,
            *args, **kwargs):
        """Just copying,
        may not be needed."""
        raise NotImplementedError
