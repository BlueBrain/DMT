import pandas as pd
from dmt.analysis import Analysis
from dmt.model.interface import interfacemethod
import numpy as np
# convenience definitions
SAMPLES = "samples"
MEAN = "mean"
STD = "std"
NSAMPLES = "nsamples"

DATA_KEYS = [SAMPLES, MEAN, STD, NSAMPLES]

example_cell_density_data = pd.DataFrame(
    {'layer': ['L1,L2,L3,L4,L5'],
     "samples": [[100, 110, 90],
                 [120, 130, 140],
                 [110, 45, 60],
                 [13, 13, 13],
                 [100, 130, 160],
                 [231, 214, 121]]})



def drop_uniform_columns(dataframe):
    """
    drops all columns from a dataframe that have only one unique value
    """
    cols = [c for c in dataframe.columns
            if len(dataframe[c].unique()) < 2]
    return (dataframe.drop(columns=cols),
            {c: dataframe[c].unique()[0] for c in cols})


def ensure_mean_and_std(data, labels):
    """
    Wherever there is no mean or std but there are datapoints(samples)
    use these datapoints to get mean and std

    assumes all are represented in form <label>_<property>
    (e.g. model_mean, bio_samples, etc.)
    """
    data = data.copy()
    for label in labels:
        def _set_axis(d):
            return 0 if hasattr(d, "__len__") else None

        def lenor1(d, axis):
            try:
                if axis is None:
                    raise AttributeError
                else:
                    return d.shape[axis]
            except AttributeError:
                return len(d) if hasattr(d, "__len__") else 1

        def fill_func_of_datapoints(series, func):
            return series.fillna({
                ind: func(datapoints[ind], axis=_set_axis(datapoints[ind]))
                for ind in data.index})

        mean = label + "_" + MEAN
        std = label + "_" + STD
        dps = label + "_" + SAMPLES
        nsamples = label + "_" + NSAMPLES
        default = pd.Series([np.nan for n in data.index])
        end_means = data.get(mean, default.copy())
        end_stds = data.get(std, default.copy())
        end_nsamps = data.get(nsamples, default.copy())
        if dps in data:
            datapoints = data[dps]
            end_means = fill_func_of_datapoints(
                    end_means, np.mean)
            end_stds = fill_func_of_datapoints(
                end_stds, np.std)
            end_nsamps = fill_func_of_datapoints(
                end_nsamps, lenor1)
        data[mean] = end_means
        data[std] = end_stds
        data[nsamples] = end_nsamps

    return data


def drop_data_entries(data, labels):
    """drop all DATA_KEYS from a dataframe"""
    data = data.copy()
    for label in labels:
        data.drop(columns=[e for e in
                           [label + "_" + entry for entry in DATA_KEYS]
                           if e in data],
                  inplace=True)
    return data


def _title(uniform_vals):
    return ','.join([str(v) for v in uniform_vals.values()])


import matplotlib.pyplot as plt


def columns(labels, data, measurement=""):
    """plot multiple column plots on the same axis"""
    data = data.fillna(np.nan)
    fig, ax = plt.subplots()
    # TODO: what to do about units? expect it in measurement?
    ax.set_ylabel(measurement)
    ind = np.arange(data.shape[0], dtype=np.float32)

    width = 1 / (len(labels) + 1)
    ax.set_xticks(ind.copy() + ((len(labels) - 1) * 0.5 * width))
    data = ensure_mean_and_std(data, labels)
    s = []
    for label in labels:

        s.append(ax.bar(ind, data[label + "_" + MEAN],
                        yerr=data[label + "_" + STD], width=width))

        ind += width

    data, uniform_vals = drop_uniform_columns(drop_data_entries(data, labels))
    plt.title(_title(uniform_vals))
    ax.legend(s, labels)
    ax.set_xlabel(', '.join(str(col) for col in data.columns))
    ax.set_xticklabels([', '.join(str(val) for val in row.values)
                        for _, row in data.iterrows()])
    return fig


class CellDensityValidation(Analysis):
    """validate cell density"""

    plotter = columns

    @interfacemethod
    def cell_density(adapter_self, query):
        """
        return the cell density of the adapted model
        for parameters specified by query
        """
        pass

    def __init__(self, *args, by=None,
                 data=example_cell_density_data, **kwargs):
        """
        by: a list of dicts of (quantities?) determining where to measure
            density. If None, will infer from data recieved.
            If no data recieved and by is None, will throw an error

        data: data to validate against
        """

        if by is None:
            if data is not None:
                by = [dict(**row) for i, row in
                      data.drop(
                          columns=[k for k in DATA_KEYS if k in data.columns])
                      .iterrowns()]
            else:
                raise ArgumentError(
                    "if 'by' is not supplied, 'data' must not be None")

        self.by = by
        self.data = data
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, adapted):
        """
        adapted: the adapted model
        """
        cell_density = [adapted.cell_density(q) for q in self.by]
        plot = self.plotter(
            ['bio', 'model'],
            pd.DataFrame({'layer': self.data['layer'],
                          'model_samples': cell_density,
                          'bio_samples': self.data['samples']}))
        return {'title': 'cell density validation',
                'plot': plot}



# temp helpers from proto-similify-improve plots branch, dmt.vtk.util
