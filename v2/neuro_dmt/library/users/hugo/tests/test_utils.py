import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal as afq
from neuro_dmt.library.users.hugo.utils import ensure_mean_and_std


def assert_frame_equal(df1, df2):
    print(df1)
    print(df2)
    return afq(df1, df2, check_like=True)


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
