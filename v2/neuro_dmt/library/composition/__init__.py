import pandas as pd
import warnings
from dmt.analysis import Analysis
from abc import abstractmethod
from neuro_dmt.library.composition.utils import DATA_KEYS, ensure_mean_and_std


# TODO: enums instead of DATA_KEYS
# TODO: figure out what to do about units
class SimpleValidation(Analysis):
    """
    base class allowing certain validations to be quickly and easily defined

    subclass needs at least a 'phenomenon' attribute, which is the name of
    the property being validated. This phenomenon attribute must be the name
    of an adapter interfacemethod of the subclass, unless the __call__ method
    is overwritten.

    TODO: work out and enforce other requirements
    TODO: make 'by' a method that can be overwritten,
          defaulting to set based on by kwarg, or else inferred by data
          this would allow defining validations with this class where 'by'
          depends on the model passed (such as a by-mtype validation)
    """

    def __init__(self, *args, data=None, **kwargs):
        """
        by: a list of dicts of (quantities?) determining where to measure
            density. If None, will infer from data recieved.
            If no data recieved and by is None, will throw an error

        data: data to validate against
        """
        if data is not None or not hasattr(self, 'data'):
            self.data = data
        if not hasattr(self, 'phenomenon'):
            raise ValueError("must have phenomenon attribute")
        super().__init__(*args, **kwargs)

    def __call__(self, *adapted):
        """
        adapted: the adapted model
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
        measured = [[self.get_measurement(model, q) for q in self.by(model)]
                    for model in adapted]
        verdict = self.verdict(*measured)
        return self._write_report(adapted, measured, verdict=verdict)

    @abstractmethod
    def get_measurement(self, model, q):
        """
        get the required measurement from the adapted model

        data must be retrieved by invoking methods of model
        required by the AdapterInterface

        """
        pass

    def by(self, model):
        """
        default method for validations: infers 'by' from validation.data
        """
        data = self.data
        if data is None:
            raise RuntimeError("{} requires data" .format(self.__class__))
        by = [dict(**row) for i, row in
              data.drop(
                  columns=[k for k in DATA_KEYS if k in data.columns])
              .iterrows()]
        return by
        pass

    def stats(self, *measured):
        """
        performs statistical tests on the measured quantities
        returns a p-value for each, and a pooled value
        default implementation: no stats
        """
        return None

    def verdict(self, *measured, stats=None, plot=None):
        """
        decides the 'pass' or 'fail' condition of the validation

        returns True if pass, False if fail, None if undecided

        default implementation: no verdict

        other implementations may decide based on
        some concrete properties of the data, the results of statistical tests,
        or by presenting the plot and requesting a manual verdict
        """
        return None

    # TODO: there may not be just one by to plot by
    # TODO: change data results and plotting format
    def _write_report(self, models, measured, verdict=None):
        report_dict = {"phenomenon": self.phenomenon}
        labels = []
        results = []

        if self.data is not None:
            bio_label = 'bio'
            results.append(ensure_mean_and_std(self.data))
            labels.append(bio_label)

        for i, m in enumerate(measured):
            model = models[i]
            df = pd.DataFrame(self.by(model))
            try:
                label = model.label
            except AttributeError:
                warnings.warn("model number {}, {} does not have label"
                              .format(i, model))
                label = 'model' + str(i)

            df['samples'] = m
            results.append(ensure_mean_and_std(df))
            labels.append(label)

        report_dict['plot'] = self.plot(
            labels, results, phenomenon=self.phenomenon)

        report_dict['data_results'] = results

        return report_dict

    def plot(self, labels, result, phenomenon):
        """default plotter, no plot"""
        return None


from neuro_dmt.library.composition.cell_density import CellDensityValidation
from neuro_dmt.library.composition.cell_density import INHRatioValidation

# TODO: metadata
