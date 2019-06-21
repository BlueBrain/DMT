import pandas as pd
from dmt.analysis import Analysis
from neuro_dmt.library.composition.utils import DATA_KEYS


class SimpleValidation(Analysis):

    def __init__(self, *args, by=None,
                 data=None, **kwargs):
        """
        by: a list of dicts of (quantities?) determining where to measure
            density. If None, will infer from data recieved.
            If no data recieved and by is None, will throw an error

        data: data to validate against
        """

        if data is None and hasattr(self, 'data'):
            data = self.data
        else:
            self.data = data

        if by is None:
            if data is not None:
                by = [dict(**row) for i, row in
                      data.drop(
                          columns=[k for k in DATA_KEYS if k in data.columns])
                      .iterrows()]
            else:
                raise RuntimeError(
                    "validation needs to know what data to request from model"
                    " if kwarg 'by' is not supplied,"
                    "kwarg 'data' must be supplied")

        self.by = by

        if not hasattr(self, 'measurement'):
            raise ValueError("must have measurement attribute")
        # TODO: ensure measurement is an interfacemethod?

        super().__init__(*args, **kwargs)

    def __call__(self, *adapted):
        """
        adapted: the adapted model
        """
        measured = [[getattr(model, self.measurement)(q) for q in self.by]
                    for model in adapted]
        return self.write_report(*measured)

    def write_report(self, *measured):
        report_dict = {"measurement": self.measurement}
        result = pd.DataFrame(self.by)
        labels = []
        if self.data is not None:
            result['bio_samples'] = self.data['samples']
            labels.append('bio')
        if len(measured) == 1:
            result['model_samples'] = measured[0]
            model_labels = ['model']
        else:
            model_labels = []
            for i, m in enumerate(measured):
                result['model{}_samples'.format(i)] = m
                model_labels.append('model{}'.format(i))

        labels = labels + model_labels

        if hasattr(self, 'plotter'):
            report_dict['plot'] = self.plotter(
                labels, result, measurement=self.measurement)

        report_dict['data_results'] = result

        return report_dict


from neuro_dmt.library.composition.cell_density import CellDensityValidation
from neuro_dmt.library.composition.cell_density import INHRatioValidation

# TODO: metadata
