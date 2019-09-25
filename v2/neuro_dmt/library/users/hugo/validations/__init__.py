import pandas as pd
import warnings
from dmt.analysis import Analysis
from abc import abstractmethod, ABC
from collections import OrderedDict
from dmt.tk.enum import DATA_KEYS, SAMPLES
from dmt.tk.data import multilevel_dataframe
from neuro_dmt.library.users.hugo.utils import\
    ensure_mean_and_std

class VERDICT:
    """enum for verdict results"""
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"
    INCONCLUSIVE = "INCONCLUSIVE"


# TODO: handle list values for queries in pandas dframes
# TODO: enums instead of DATA_KEYS
# TODO: figure out what to do about units
#       OPTION1: put in measurement parameters
#       OPTION2: put in phenomenon, clarify in adapter
class SimpleValidation(Analysis, ABC):
    """
    base class allowing certain validations to be quickly and easily defined

    a subclass needs to define at least get_measurement, while default options
    exist for measurement_parameters, stats, verdict and plot.
    Overwrite those to customize the validation

    """

    def __init__(self, *args, data=None, **kwargs):
        """
        Arguments:
            data: DataFrame: data to validate against
        """
        self.data = data
        if not hasattr(self, 'phenomenon'):
            warnings.warn(Warning(
                "{} does not have a phenomenon, defaulting to 'Not Provided'"
                .format(self)))
            self.phenomenon = "Not Provided"
        super().__init__(*args, **kwargs)

    # TODO: implement a check that ensures any method/attribute calls
    #       on 'model' are documented in the AdapterInterface
    #       could be done by passing AdapterInterface through methods and
    #       catching AttributeError
    @abstractmethod
    def get_measurement(self, model, measurement_parameters):
        """
        get the required measurement from the adapted model
        abstract, must be overwritten in subclass
        data must be retrieved by invoking methods of model
        required by the AdapterInterface

        Arguments:
           model: model from which to extract the data
           measurement_parameters:
                  dict or dict-like,
                  an element of self.measurements_parameters(model),
                  additional data on where
                  and what to extract (region, mtype, layer, column...)

        Returns:
           samples: one or more values representing the values retrieved
        """
        raise NotImplementedError()

    def measurements_parameters(self, model):
        """
        data governing what to query in get_measurement
        (region, layer, mtype, etc.)
        default: infers from self.data

        Arguments:
           model: the model from which the data will be collected

        Returns:
           list of dict, each dict containing properties as key-value pairs

        TODO: formally document format
        """
        # TODO: cache measurement_parameters
        data = self.data
        if data is None:
            raise TypeError("{} requires data, or "
                            "a different measurements_parameters method"
                            .format(self.__class__))
        stripped_data = data.drop(
            columns=[k for k in DATA_KEYS if k in data.columns])
        if stripped_data.shape[1] == 0 or stripped_data.shape[1] == 0:
            warnings.warn(
                Warning(
                    "data contains no information besides values, "
                    "result will sample whole model"))
            return [{}]

        measurements_parameters = [dict(**row)
                                   for i, row in stripped_data.iterrows()]
        return measurements_parameters

    def get_stats(self, *measurements):
        """
        statistical tests of measured quantities
        default: no test

        Arguments:
            measurements: the measured quantities for each model

        Returns:
            (DataFrame) a p-value for each measurement of each model
            optionally a pooled p-value for each model

        """
        return None

    def get_verdict(self, report):
        """
        decides whether the validation passes or fails
        default: no verdict

        Arguments:
            report: validation Report. Will have plot, stats, data_results
                    to be used to determine verdict
        Returns:
            VERDICT.PASS, VERDICT.FAIL, VERDICT.NA or VERDICT.INCONCLUSIVE
        """
        return VERDICT.NA

    # TODO: should I be consistent in naming, call this get_plot
    def plot(self, labels, result):
        """
        plots the results of the validation
        default: no plot

        Arguments:
            labels : a label for each element in result
            result: a list of DataFrames
        """
        return None

    # TODO: change data results and plotting format
    def _get_report(self, measurements):
        """
        write and return a report of the validation

        Arguments:
            measurements: the measured quantities for each model, pd.DataFrame

        Returns
            a Report instance with attributes of plotting, etc.
        """

        report = Report()
        report.phenomenon = self.phenomenon
        labels = []
        results = []

        if self.data is not None:
            bio_label = 'bio'
            results.append(ensure_mean_and_std(self.data))
            labels.append(bio_label)

        for label, measurement in measurements:
            results.append(ensure_mean_and_std(measurement))
            labels.append(label)
        print("plotting")
        plot = self.plot(labels, results)
        stats = self.get_stats(*measurements)
        report.plot = plot
        report.stats = stats

        report.data_results = [
            (label, results[i]) for i, label in enumerate(labels)]

        # TODO: should verdict be passed the whole report?
        #       it would allow e.g. showing plot and requesting user verdict
        report.verdict = self.get_verdict(report)
        return report

    def __call__(self, *adapted):
        """
        Arguments:
            adapted: the adapted model(s)
        """
        # TODO: wrap the adapted model in an 'adapterchecker' which
        #       checks that all the methods required by the
        #       AdapterInterface are there
        #       forwards all method calls to the adapted model
        #       raises a warning if a method not declared in the AdapterInterface
        #       is called on it, and raises an appropriate error when
        #       a method not declared in AdapterInterface is called and the
        #       adapted model does not have it
        # TODO: should mparam keys be restricted to the values of an enum?
        #       error message should indicate that to use key you should add it
        #       to enum
        # TODO: perhaps parameters should be ordered, leads to cleaner plotting
        #       (e.g. layer, mtype vs mtype, layer)
        models_measurements = []
        for i, model in enumerate(adapted):

            measurements_parameters = self.measurements_parameters(model)
            try:
                label = model.label
            except AttributeError:
                warnings.warn("model number {}, {} does not have label"
                              .format(i, model))
                label = 'model_{}'.format(i)

            sampleslist = []
            nmeasurements = len(measurements_parameters)
            for i, parameters in enumerate(
                    self.measurements_parameters(model)):
                progress = i / nmeasurements
                print(label, ": {0:.2%}".format(progress), end="\r")
                sampleslist.append(
                    self.get_measurement(model, parameters))

            model_measurements = (
                multilevel_dataframe(measurements_parameters))
            model_measurements[SAMPLES] = sampleslist
            models_measurements.append((label, model_measurements))

        return self._get_report(models_measurements)


class Report:
    # TODO: __repr__ method
    """validation report,
    for now just contains the results of the validation"""
    pass



from .cell_density import CellDensityValidation, INHRatioValidation

# TODO: metadata
