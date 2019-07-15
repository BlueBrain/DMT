import pandas as pd
import numpy as np
import pytest as pyt
from pandas.testing import assert_frame_equal as afq
from neuro_dmt.library.users.hugo.validations import \
    SimpleValidation, Report, VERDICT


def assert_frame_equal(df1, df2):
    print(df1)
    print(df2)
    return afq(df1, df2, check_like=True)


class _TestValidation(SimpleValidation):
    phenomenon = "Test"

    class AdapterInterface:
        def v(m, q):
            pass

    def get_measurement(self, m, q):
        return m.v(q)


class TestSimpleValidation:

    class TestInitialzation:

        def test_default_phenomenon(self):

            class _TestValidationNoPhenom(SimpleValidation):
                def get_measurement(self, m, q):
                    pass

            with pyt.warns(Warning):
                assert _TestValidationNoPhenom().phenomenon == "Not Provided"

        def test_sets_data(self):
            data = pd.DataFrame({"buh": [1, 2, 3, 4]})
            assert all(_TestValidation(data=data).data == data)

    class TestDefaultBy:
        """test the default implementation of the 'by' method"""
        # TODO: should only data keys, empty dataframe, and no data all
        #       give the same result? which result?

        def test_error(self):
            dummy_object = ''
            with pyt.raises(TypeError):
                _TestValidation().by(dummy_object)

        def test_data_with_data_keys(self):
            data = pd.DataFrame({"mean": [1, 2, 3, 4, 5],
                                 'blarg': [11, 12, 13, 14, 15]})
            by = _TestValidation(data=data).by('')
            assert by == [{'blarg': v} for v in data['blarg']]

        def test_data_only_data_keys(self):
            data = pd.DataFrame({"mean": [1, 2, 3, 4, 5]})
            with pyt.warns(Warning):
                by = _TestValidation(data=data).by('')
            assert by == [{}]

        def test_data_empty_dataframe(self):
            data = pd.DataFrame()
            with pyt.warns(Warning):
                by = _TestValidation(data=data).by('')
            assert by == [{}]

    class TestOtherDefaults:

        def test_stats(self):
            assert _TestValidation().get_stats() is None

        def test_verdict(self):
            assert _TestValidation().get_verdict() is VERDICT.NA

        def test_plot(self):
            assert _TestValidation().plot('', '') is None

    class TestCall:

        def test_call_emptydata(self):

            class DummyModel:
                label = "dummy"

                def v(self, q):
                    return 1.0

            data = pd.DataFrame({'mean': [1.0], 'b': [1.0]})
            report = _TestValidation(data=data)(DummyModel())
            assert isinstance(report, Report)
            assert report.phenomenon == _TestValidation.phenomenon
            assert report.plot is None
            assert report.stats is None
            assert report.data_results[0][0] == 'bio'
            assert_frame_equal(
                report.data_results[0][1],
                pd.DataFrame({'mean': [1.0], 'std': [np.nan],
                              'nsamples': [np.nan], 'b': [1.0]}))
            assert report.data_results[1][0] == 'dummy'
            assert_frame_equal(
                report.data_results[1][1],
                pd.DataFrame({'mean': [1.0], 'std': [0.0], 'nsamples': [1.],
                              'b': [1.0], 'samples': [1.0]}))
