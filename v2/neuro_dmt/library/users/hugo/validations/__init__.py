import pandas as pd
import warnings
from enum import Enum
from dmt.analysis import Analysis
from abc import abstractmethod, ABC
from neuro_dmt.library.users.hugo.utils import\
    DATA_KEYS, ensure_mean_and_std


class VERDICT:
    """enum for verdict results"""
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"
    INCONCLUSIVE = "INCONCLUSIVE"


# TODO: enums instead of DATA_KEYS
# TODO: figure out what to do about units
class SimpleValidation(Analysis, ABC):
    """
    base class allowing certain validations to be quickly and easily defined

    a subclass needs to define at least get_measurement, while default options
    exist for by, stats, verdict and plot.
    Overwrite those to customize the validation

    TODO: work out and enforce other requirements
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
    def get_measurement(self, model, query):
        """
        get the required measurement from the adapted model
        abstract, must be overwritten in subclass
        data must be retrieved by invoking methods of model
        required by the AdapterInterface

        Arguments:
           model: model from which to extract the data
           query: dict or dict-like,
                  an element of self.by, additional data on where
                  and what to extract (region, mtype, layer, column...)

        Returns:
           samples: one or more values representing the values retrieved
        """
        raise NotImplementedError()

    def by(self, model):
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
        # TODO: cache by
        data = self.data
        if data is None:
            raise TypeError("{} requires data" .format(self.__class__))
        stripped_data = data.drop(
            columns=[k for k in DATA_KEYS if k in data.columns])
        if stripped_data.shape[1] == 0 or stripped_data.shape[1] == 0:
            warnings.warn(
                Warning(
                    "data contains no information besides values, "
                    "result will sample whole model"))
            return [{}]

        by = [dict(**row) for i, row in stripped_data.iterrows()]
        return by

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

    def get_verdict(self, *measurements, stats=None, plot=None):
        """
        decides whether the validation passes or fails
        default: no verdict

        Arguments:
            measurements: the measured quantities for each model
            stats: p-values for measurements
            plot: plot of validation results

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


    # TODO: there may not be just one by to plot by
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

        plot = self.plot(labels, results)
        stats = self.get_stats(*measurements)
        report.plot = plot
        report.stats = stats
        # TODO: OrderedDict?
        report.data_results = [
            (label, results[i]) for i, label in enumerate(labels)]

        # TODO: should verdict be passed the whole report?
        #       it would allow e.g. showing plot and requesting user verdict
        report.verdict = self.get_verdict(*measurements,
                                          stats=stats, plot=plot)
        return report

    def __call__(self, *adapted):
        """
        Arguments:
            adapted: the adapted model(s)
        """
        # TODO: wrap the adapted model in an 'adapterchecker' which
        #       checks that all the methods required by the AdapterInterface are there
        #       forwards all method calls to the adapted model
        #       raises a warning if a method not declared in the AdapterInterface
        #       is called on it, and raises an appropriate error when
        #       a method not declared in AdapterInterface is called and the
        #       adapted model does not have it
        # TODO: should query keys be restricted to the values of an enum?
        #       error message should indicate that to use key you should add it
        #       to enum
        models_measurements = []
        for i, model in enumerate(adapted):
            by = self.by(model)
            try:
                label = model.label
            except AttributeError:
                warnings.warn("model number {}, {} does not have label"
                              .format(i, model))
                label = 'model_{}'.format(i)

            model_measurements = (label, pd.DataFrame(by).assign(
                samples=[self.get_measurement(model, q)
                         for q in self.by(model)]))
            models_measurements.append(model_measurements)

        return self._get_report(models_measurements)


class Report:
    # TODO: __repr__ method
    """validation report,
    for now just contains the results of the validation"""
    pass



from .cell_density import CellDensityValidation, INHRatioValidation

# TODO: metadata
