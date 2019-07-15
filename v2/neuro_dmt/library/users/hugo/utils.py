import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dmt.tk.plotting import golden_figure


SAMPLES = "samples"
MEAN = "mean"
STD = "std"
NSAMPLES = "nsamples"

DATA_KEYS = [SAMPLES, MEAN, STD, NSAMPLES]
# keys reserved for data in the dataframes
# TODO: this should be available as an enum. These keys are not specific
#       to neuroscience, so the logical place would be in dmt.tk


def drop_uniform_columns(dataframe):
    """
    drops all columns from a dataframe that have only one unique value
    (used to ensure uniform columns go into the title rather than the x axis)

    Args:
        dataframe : pandas DataFrame

    Returns:
        the dataframe with the uniform columns values dropped
        dict of {column: value} containing the values of
        the uniform columns
    """
    cols = [c for c in dataframe.columns
            if len(dataframe[c].unique()) < 2]
    values = {c: dataframe[c].unique()[0] for c in cols}
    out_dataframe = dataframe.drop(columns=cols)
    return out_dataframe, values


def ensure_mean_and_std(data):
    """
    Wherever there is no mean or std but there are datapoints(samples)
    use these datapoints to get mean and std

    where there none of these, leave np.nan

    Args:
        data: pandas DataFrame

    Returns:
        a new dataframe with 'mean', 'std' and 'nsamples' columnss, where
        the values are filled in based on the 'samples' column

    """

    def _set_axis(d):
        """return 0 if d is iterable, else None"""
        return 0 if hasattr(d, "__len__") else None

    def lenor1(d, axis):
        """return the length of d along axis 0 if it is iterable,
        or 1 if it is not"""
        return len(d) if hasattr(d, "__len__") else 1

    def fill_func_of_datapoints(datapoints, series, func):
        """fill the NaN values of series with some
        function func of the corresponding datapoints"""
        return series.fillna({
            ind: func(datapoints[ind], axis=_set_axis(datapoints[ind]))
            for ind in data.index})

    default = pd.Series([np.nan for n in range(data.shape[0])])
    end_means = data.get(MEAN, default.copy())
    end_stds = data.get(STD, default.copy())
    # TODO: pandas24 allows nan integer
    end_nsamps = data.get(NSAMPLES, default.copy())
    if SAMPLES in data:
        datapoints = data[SAMPLES]
        end_means = fill_func_of_datapoints(
            datapoints, end_means, np.mean)
        end_stds = fill_func_of_datapoints(
            datapoints, end_stds, np.std)
        end_nsamps = fill_func_of_datapoints(
            datapoints, end_nsamps, lenor1)
    return data.assign(**{MEAN: end_means,
                          STD: end_stds,
                          NSAMPLES: end_nsamps})


def drop_data_entries(data):
    """drop all DATA_KEYS from a dataframe"""
    return data.drop(columns=[e for e in
                              [entry for entry in DATA_KEYS]
                              if e in data])


def _title(phenomenon, uniform_vals):
    """
    generates a plot title based on
    the phenomenon displayed and those attributes
    which are the same for all data
    Arguments:
        phenomenon: name of the phenomenon plotted (e.g. cell density)
        uniform_vals: attributes of the data that are constant across allow
                      datapoints
                      (might be region: SSp-ll for a validation of SSp-ll)
    Returns:
        a string to use as title
    """
    if len(uniform_vals) == 0:
        return phenomenon

    return phenomenon + ' for ' + ','.join(
        ["{}: {}".format(k, v)
         for k, v in uniform_vals.items()])


# TODO: kwarg to plot datapoints
# TODO: automatically adjust font size to prevent overlap
def plot_columns(labels, data, phenomenon=""):
    """plot multiple column plots on the same axis"""
    data = [d.fillna(np.nan) for d in data]
    fig, ax = golden_figure()
    # TODO: what to do about units? expect it in phenomenon?
    ax.set_ylabel(phenomenon)
    # TODO: deal with case where x-values are not same for all data
    plotby, uniform_vals = drop_uniform_columns(drop_data_entries(data[0]))
    ind = np.arange(plotby.shape[0], dtype=np.float32)

    width = 1 / (len(labels) + 1)
    ax.set_xticks(ind.copy() + ((len(labels) - 1) * 0.5 * width))
    s = []
    for i, label in enumerate(labels):
        # TODO: plot confidence interval instead of std
        s.append(ax.bar(ind, data[i][MEAN],
                        yerr=data[i][STD], width=width))

        ind += width

    plt.title(_title(phenomenon, uniform_vals))
    ax.legend(s, labels)
    ax.set_xlabel(', '.join(str(col) for col in plotby.columns))
    ax.set_xticklabels([', '.join(str(val) for val in row.values)
                        for _, row in plotby.iterrows()])
    return fig, ax
