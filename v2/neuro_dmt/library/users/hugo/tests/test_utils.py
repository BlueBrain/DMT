import pandas as pd
import numpy as np
import pytest as pyt
import matplotlib.pyplot as plt
from pandas.testing import assert_frame_equal as afq
from pandas.testing import assert_series_equal as asq
from neuro_dmt.library.users.hugo.utils import\
    ensure_mean_and_std, plot_columns


def assert_frame_equal(df1, df2):
    print(df1)
    print(df2)
    return afq(df1, df2, check_like=True)


def assert_series_equal(s1, s2):
    print(s1)
    print(s2)
    return asq(s1, s2)


def assert_iterables_equal(e1, e2):
    print(e1)
    print(e2)
    return len(e1) == len(e2) and all(e2[i] == v for i, v in enumerate(e1))


class Test_ensure_mean_and_std:

    def test_only_one_sample(self):
        in_frame = pd.DataFrame({"samples": [1, 2, 3, 4, 5]})
        out_frame = ensure_mean_and_std(in_frame)
        assert_frame_equal(out_frame, pd.DataFrame(
            {'mean': [1.0, 2.0, 3.0, 4.0, 5.0],
             'std': [0.0, 0.0, 0.0, 0.0, 0.0],
             'nsamples': [1.0, 1.0, 1.0, 1.0, 1.0],
             "samples": [1, 2, 3, 4, 5]}))

    def test_list_samples(self):
        in_frame = pd.DataFrame({'samples': [
            [1.0, 2.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]})
        out_frame = ensure_mean_and_std(in_frame)
        assert_frame_equal(out_frame,
                           pd.DataFrame({'mean': [1.5, 5.0, 8.0],
                                         'std': [np.std(s)
                                                 for s in
                                                 in_frame['samples']],
                                         'nsamples': [2., 3., 3.],
                                         'samples': [
                                             [1.0, 2.0],
                                             [4.0, 5.0, 6.0],
                                             [7.0, 8.0, 9.0]]}))

    def test_empty(self):
        assert_frame_equal(ensure_mean_and_std(pd.DataFrame()),
                           pd.DataFrame(
                               columns=['mean', 'nsamples', 'std'],
                               dtype='float64'))

    def test_mean_and_std_no_samples(self):
        in_frame = pd.DataFrame({"mean": [1, 2, 3, 4], "std": [1, 2, 3, 4]})
        out_frame = ensure_mean_and_std(in_frame)
        assert_frame_equal(
            out_frame,
            pd.DataFrame({
                "mean": [1, 2, 3, 4],
                "std": [1, 2, 3, 4],
                "nsamples": [np.nan, np.nan, np.nan, np.nan]}))

    # TODO: what behavior when samples and aggregates disagree?


class Test_plot_columns:

    def test_one_dataset(self):
        plt.clf()
        test_labels = ['test']
        test_data = pd.DataFrame({'measurement_property': ['a', 'b', 'c'],
                                  'mean': [10, 20, 30],
                                  'std': [1, 2, 3]})
        test_phenomenon = 'cd'
        fig, ax = plot_columns(test_labels, [test_data],
                               phenomenon=test_phenomenon)
        assert ax.get_title() == test_phenomenon
        assert ax.get_ylabel() == test_phenomenon
        assert ax.get_xlabel() == 'measurement_property'
        assert_iterables_equal(ax.get_xticklabels(),
                               test_data.measurement_property)
        handles, labels = ax.get_legend_handles_labels()
        assert labels == test_labels

    def test_two_datasets(self):
        plt.clf()
        test_labels = ['test1', 'test2']
        test_data = [pd.DataFrame({'measurement_property': ['a', 'b', 'c'],
                                   'mean': [10, 20, 30],
                                   'std': [1, 2, 3]}),
                     pd.DataFrame({'measurement_property': ['a', 'b', 'c'],
                                   'mean': [60, 20, 60],
                                   'std': [1, 2, 3]})]
        test_phenomenon = 'cd'
        fig, ax = plot_columns(test_labels, test_data,
                               phenomenon=test_phenomenon)
        assert ax.get_title() == test_phenomenon
        assert ax.get_ylabel() == test_phenomenon
        assert ax.get_xlabel() == 'measurement_property'
        assert_iterables_equal(ax.get_xticklabels(),
                               test_data[0].measurement_property)
        handles, labels = ax.get_legend_handles_labels()
        assert labels == test_labels

    @pyt.mark.xfail
    def test_confidence_interval(self):
        """test that errorbar reflects a 95% confidence interval"""
        test_labels = ['test']
        test_data = pd.DataFrame({'measurement_property': ['a', 'b', 'c'],
                                  'mean': [10, 20, 30],
                                  'std': [1, 2, 3],
                                  'nsamples': [4, 1, 2]})

        z_stat = 1.96  # for 95% CI
        confidence = z_stat /\
            test_data['std'] / np.sqrt(test_data['nsamples'])

        test_phenomenon = 'cd'
        fig, ax = plot_columns(test_labels, [test_data],
                               phenomenon=test_phenomenon)
        handles, labels = ax.get_legend_handles_labels()
        segments = handles[0].errorbar.lines[2][0].get_segments()
        segment_lengths = [s[1, 1] - s[0, 1] for s in segments]
        assert assert_iterables_equal(segment_lengths, confidence)

    @pyt.mark.xfail
    def test_no_std(self):
        test_labels = ['test']
        test_data = pd.DataFrame({'measurement_property': ['a', 'b', 'c'],
                                  'mean': [10, 20, 30]})
        test_phenomenon = 'cd'
        fig, ax = plot_columns(test_labels, [test_data],
                               phenomenon=test_phenomenon)
        handles, labels = ax.get_legend_handles_labels()
        assert handles[0].errorbar is None
