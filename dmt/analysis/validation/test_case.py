""" Some base classes for validations.

Implementation Notes
--------------------------------------------------------------------------------
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of a validation class will accept a data object.
"""

from abc import abstractmethod
from dmt.model import Callable, AIBase
from dmt.data import ReferenceData
from dmt.analysis import Analysis
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class ValidationTestCase(Analysis):
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
        __doc__="p-value threshold to determine if a validation passed or not."
    )

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    def get_validation_data(self):
        """..."""
        try:
            return self.reference_data.data
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_data(),
                "Could not get data from reference data.",
                "\t AttributeError: {}".format(e)
            )
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

        real_measurement = self.primary_dataset
        if real_measurement is not None:
            delta_mean = abs(
                model_data["mean"] - real_measurement.data["mean"]
            )
            stdev = sqrt(
                model_data["std"]**2 + real_measurement.data["std"]**2
            )
            z_score = delta_mean / stdev
            pval = 1. - erf(z_score)
            return pd.DataFrame(dict(
                delta_mean = delta_mean,
                std = stdev,
                z_score = z_score,
                pvalue = pval
            ))
        return pd.DataFrame()

    def pvalue(self, model_measurement):
        """Scalar valued  p-value.
        If measurement is vector-valued, then a pooled value will be returned.
        Default implementation, Override for your model_measurement
        """
        from dmt.vtk.statistics import FischersPooler
        N = model_measurement.data.shape[0]
        pvt = self.pvalue_table(model_measurement)

        if N == 1:
            return float(pvt.pvalue)
        else:
           return FischersPooler.eval(pvt.pvalue)


    @property
    @abstractmethod
    def primary_dataset(self):
        """..."""
        pass

@document_fields
class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.
    """
    def __init__(self, *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        if 'validated_phenomenon' in kwargs:
            kwargs["phenomena"] = {kwargs['validated_phenomenon']}
        if 'phenomenon' in kwargs:
            kwargs["phenomena"] = {kwargs['phenomenon']}
        super().__init__(*args, **kwargs)

    def plot(self, model_measurement, *args, **kwargs):
        """Plot the data."""
        name = model_measurement.phenomenon.name
        kwargs['output_dir_path'] = self.output_dir_path
        kwargs['title']  = name
        kwargs['xlabel'] = model_measurement.parameter
        kwargs['ylabel'] = "{} / [{}]".format("mean {}".format(name.lower()),
                                           model_measurement.units)
        kwargs.update(self.plot_customization)
        plotter = self.plotter_type(Record(data=model_measurement.data,
                                           label=model_measurement.label))\
                      .comparing("dataset")\
                      .against(self.validation_data)\
                      .for_given(list(self.spatial_parameters)[0])\
                      .with_customization(**kwargs)

        return plotter.plot()


    @classmethod
    def get_caption(cls, model_measurement):
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
            .format(model_measurement.phenomenon.title,
                    model_measurement.phenomenon.description,
                    model_measurement.method)

