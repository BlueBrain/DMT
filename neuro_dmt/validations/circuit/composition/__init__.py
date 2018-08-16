"""Code relevant for validation of composition phenomena"""

from abc import abstractmethod
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils.brain_region import BrainRegion
from dmt.vtk.plotting import Plot
from dmt.vtk.utils.descriptor import ClassAttribute, Field, document_fields
from dmt.vtk.utils.collections import Record
from dmt.vtk.judgment.verdict import Verdict

@document_fields
class SpatialCompositionValidation:
    """Validates a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated.
    """
    plotter_type = ClassAttribute(
        __name__ = "plotter_type",
        __type__ = type,
        __is_valid_value__ = lambda ptype: issubclass(ptype, Plot),
        __doc__ = """A subclass of {} to be used plot the results of
        this validation.""".format(Plot)
    )
    region_type = ClassAttribute(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_value__ = lambda rtype: issubclass(rtype, BrainRegion),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- region type is the type of these
        location. For example, you may want cell density as a function of
        CorticalLayer."""
    )
    def __init__(self, validation_data, *args, **kwargs):
       """This validation will be made against multiple datasets. Each dataset
       should provide a 'Record' as specified below.

       Arguments
       -------------------------------------------------------------------------
       validation_data :: List[Record(measurement_label :: String,
       ~                              region_label :: String,
       ~                              data :: DataFrame["region", "mean", "std"])],
       ~                              citation :: Citation,
       ~                              what :: String)]
       -------------------------------------------------------------------------

       Keyword Arguments
       -------------------------------------------------------------------------
       p_value_threshold :: Float #optional
       output_dir_path :: String #optional
       report_file_name :: String #optional
       plot_customization :: Dict #optional
       """
       kwargs.update({'validation_data': validation_data})
       super(SpatialCompositionValidation, self).__init__(*args, **kwargs)

       self.p_value_threshold = kwargs.get('p_value_threshold', 0.05)
       self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
       self.report_file_name = kwargs.get('report_file_name', 'report.html')
       self.plot_customization = kwargs.get('plot_customization')

    def plot(self, model_measurement, *args, **kwargs):
        """Plot the data."""
        plotter = self.plotter_type(**plot_customization)
        plotting_datasets = model_measurement + self.validation_data
        plotter.plot(plotting_datasets)

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

        Parameters
        ------------------------------------------------------------------------
        model_mesaurement :: Record(...)
        """
        from scipy.special import erf
        from np import abs, sqrt

        real_measurement = self.validated_data[0]
        N = real_measurement.data.shape[0]
        delta_mean \
            = abs(model_measurement.data.mean - real_measurement.data.mean)
        stdev \
            = sqrt(model_measurement.data.std**2 + real_measurement.data.std**2)
        z_score = delta_mean / stdev
        pval = 1. - erf(z_score)
        return pd.DataFrame(dict(
            delta_mean = delta_mean,
            std = stdev,
            z_score = z_score,
            pvalue = pval
        ))

    def pvalue(self, model_measurement):
        """Scalar valued  p-value.
        If measurement is vector-valued, then a pooled value will be returned.
        """
        from dmt.vtk.statistics import FischersPooler
        N = model_measurement.data.shape[0]
        pvt = self.pvalue_table(model_measurement)

        if N == 1:
            return float(pvt.pvalue)
        else:
           return FischersPooler.eval(pvt.pvalue)


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


    @abstractmethod
    def get_measurement(self, circuit_model):
        """Get the measurement to be validated."""
        pass

    @abstractmethod
    def get_label(self, circuit_model):
        """Get a label for the measurement validated."""
        pass

    def __call__(self, circuit_model, *args, **kwargs):
        """...Call Me..."""
        save = kwargs.get('save', False) #Or should we save by default?
        model_measurement = self.get_measurement(circuit_model)
        model_label = self.get_label(circuit_model)

        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)

        report = ValidationReport(
            validated_phenomenon = self.validated_phenomenon.title,
            validated_image_path = self.plot(model_measurement),
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_data,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval
        )

        if save:
            report.save(
                output_dir_path = kwargs.get('output_dir_path',
                                             self.output_dir_path)
                report_file_name = kwargs.get('report_file_name',
                                              self.report_file_name)
            )
        return report
