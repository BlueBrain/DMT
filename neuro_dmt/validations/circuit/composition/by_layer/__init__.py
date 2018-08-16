"""Utilities for circuit composition by layer."""
from abc import abstractmethod
import pandas as pd
import numpy as np
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, document_fields
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import CompositionReport
from neuro_dmt.utils.brain_region import BrainRegion


@document_fields
class CompositionPhenomenonValidation:
    """Validation of a single circuit composition phenomenon."""
    region_type = Field(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_value__ = lambda rtype: issubclass(rtype, BrainRegion),
        __doc__ = """Composition phenomena are to measured as a function of
        a region type, for example cell density in the cortex as a functionf of
        'CorticalLayer'"""

    def __init__(self, validation_data, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(measurement_label :: String,
        ~                              region_label :: String,
        ~                              data :: DataFrame["region", "mean", "std"])],
        ~                              citation :: Citation,
        ~                              what :: String)]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional
        report_file_name :: String #optional
        plot_customization :: Dict #optional
        """

        #add keyword arguments and call super intiialization
        kwargs.update({'validation_data': validation_data})
        super(CompositionValidation, self).__init__(*args, **kwargs)

        self.p_value_threshold = kwargs.get('p_value_threshold', 0.05)
        self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
        self.report_file_name = kwargs.get('report_file_name', 'report.html')
        self.plot_customization = kwargs.get('plot_customization', {})

    @classmethod
    def get_caption(cls, model_measurement):
        """Caption for a plot.
        This method produces a caption from a measurement of the
        model.

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

    def plot(self, model_measurement, *args, **kwargs):

        plotting_datas = [model_measurement] + self.validation_data

    def probability_of_validity(self, model_measurement):
        """Probability that a model measurement is valid.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(...)
        """
        from dmt.vtk.statistics import FischersPooler
        from scipy.special import erf

        real_measurement = self.validated_data[0]
        delta_mean = np.abs(model_measurement.data.mean -
                            real_measurement.data.mean)
        stdev = np.sqrt(real_measurement.data.std**2 +
                         model_measurement.data.std**2)
        z_score = delta_mean / stdev
        p_values = pd.DataFrame(dict(
            region = real_measurement.data.index,
            delta_mean = delta_mean,
            std = stdev,
            z_score = z_score,
            p_value = 1. - erf(z_score)
        ))
        return Record(
            p_value_by_region = p_values,
            pooled = float(FischersPooler.eval(p_values.p_value))
        )

    def get_verdict(self, p):
        """Is a measurement with p-value p valid?

        Parameters
        ------------------------------------------------------------------------
        p :: Float #p value of an experimental measurement.
        """
        if np.isnan(p):
            return Verdict.NA
        if p > self.p_value_threshold:
            return Verdict.PASS
        if p <= self.p_value_threshold:
            return Verdict.FAIL
        return Verdict.INCONCLUSIVE

    @abstractmethod
    def get_measurement(self, circuit_model):
        """Get the measurement to be validated."""
        pass

    def __call__(self, circuit_model, *args, **kwargs):
        """...Call Me..."""
        output_dir_path = kwargs.get('output_dir_path', self.output_dir_path)
        report_file_name = kwargs.get('report_file_name', self.report_file_name)

        model = self.adapted(circuit_model) #and use model as you wish!
        model_measurement = self.get_measurement(circuit_model)
        model_label = model.get_label()

        p_val = self.probability_of_validity(model_measurement)
        verdict = self.get_verdict(p_val)

        return CompositionReport(
            validated_phenomenon = self.validated_phenomenon.title,
            validated_image_path = self.plot(model_measurement),
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_data,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            p_value = p_val.pooled
        )
