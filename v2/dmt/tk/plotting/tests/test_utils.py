import pandas as pd
import pandas.testing as pdt
from dmt.tk.enum import MEAN, STD
from collections import OrderedDict
from dmt.tk.plotting.utils import collapse_dataframe_column, pivot_table


def assert_odicts_of_pd_equal(d1, d2):
    try:
        assert d1.keys() == d2.keys()
        for v1, v2 in zip(d1.values(), d2.values()):
            pdt.assert_series_equal(v1, v2)
    except AssertionError as ae:
        print(d1.keys(), "\n", d2.keys())
        print(d1.values(), "\n\n\n", d2.values())
        raise ae


# TODO: dicts and strings
class Test_collapse_dataframe_column:

    def test_given_strings(self):
        tdf = pd.DataFrame(dict(pre=['a', 'b', 'c', 'd']))
        coldf, groups = collapse_dataframe_column(tdf,  'pre')
        pd.testing.assert_frame_equal(coldf, tdf)
        rows = [r for _, r in tdf.iterrows()]
        assert coldf.columns[0] == 'pre'
        assert_odicts_of_pd_equal(
            groups,
            OrderedDict([(base, rows[i]) for i, base in enumerate(tdf.pre)]))

    def test_given_dicts(self):
        tdf = pd.DataFrame(OrderedDict(
            [(('pre', 'layer'), range(4)),
             (('pre', 'mtype'), ['a', 'b', 'c', 'd'])]))
        df, groups = collapse_dataframe_column(tdf,  'pre')

        edf = pd.DataFrame({'pre: layer, mtype':
                            [str(l) + ", " + str(m)
                             for l, m in enumerate(['a', 'b', 'c', 'd'])]})
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
        assert_odicts_of_pd_equal(
            groups,
            OrderedDict((v, tdf.iloc[i])
                        for i, v in enumerate(edf[edf.columns[0]])))

    def test_mismatched_dicts(self):
        tdf = pd.DataFrame(OrderedDict([
            (('buh', 'layer'), ['1', '3', '2', '3']),
            (('buh', 'mtype'), ['a', None, 'b', 'c']),
            (('buh', 'unecessary'), [None, None, None, 'detail'])]))

        edf = pd.DataFrame({
             'buh: layer, mtype, unecessary': [
                '1, a, _',
                '3, _, _',
                '2, b, _',
                '3, c, detail']})
        df, groups = collapse_dataframe_column(tdf, 'buh')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
        assert_odicts_of_pd_equal(
            groups, OrderedDict((v, tdf.iloc[i])
                                for i, v in enumerate(edf[edf.columns[0]])))

    def test_deeper(self):
        tdf = pd.DataFrame(OrderedDict([
            (('a', 'b', 'c'), [1, 2, 3]),
            (('a', 'b', 'd'), [1, 3, 4]),
            (('a', 'c', 'g'), [2, 3, 4])]))
        edf = pd.DataFrame({
            'a: {b: {c, d}, c: g}':
            ['1, 1, 2', '2, 3, 3', '3, 4, 4']})
        df, groups = collapse_dataframe_column(tdf, 'a')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
        assert_odicts_of_pd_equal(
            groups, OrderedDict((v, tdf.iloc[i])
                                for i, v in enumerate(edf[edf.columns[0]])))


class Test_pivot_table:
    """
    fromgrps and togrps already tested by collapse_dataframe_column
    TODO: what is the best way to test in such a situation
    """

    def test_basic(self):
        df = pd.DataFrame(OrderedDict([
            (MEAN, [1, 2, 1, 2]),
            ('pre', ['a', 'a', 'b', 'b']),
            ('post', ['a', 'b', 'a', 'b'])]))
        table = pivot_table(df, 'pre', 'post', MEAN)[0]
        pd.testing.assert_frame_equal(
            table,
            df.pivot_table(index='pre', columns='post',
                           values=MEAN))

    def test_2_level_columns(self):
        df = pd.DataFrame(OrderedDict([
            ((MEAN, ''), [1, 2, 1, 2]),
            ((STD, ''), [1, 2, 3, 1]),
            (('pre', 'mtype'), ['a', 'a', 'b', 'b']),
            (('post', 'mtype'), ['a', 'b', 'a', 'b'])]))
        table = pivot_table(df, 'pre', 'post', MEAN)[0]
        edf = pd.DataFrame({
            'pre: mtype': ['a', 'a', 'b', 'b'],
            'post: mtype': ['a', 'b', 'a', 'b'],
            MEAN: [1, 2, 1, 2]})\
            .pivot_table(index='pre: mtype',
                         columns='post: mtype',
                         values=MEAN)
        print(table, "\n\n", edf)
        pd.testing.assert_frame_equal(
            table, edf)

    def test_duplicate_pathways(self):
        df = pd.DataFrame(OrderedDict([
            ((MEAN, ''), [1, 2, 1, 2, 3]),
            ((STD, ''), [1, 2, 3, 1, 3]),
            (('pre', 'mtype'), ['a', 'a', 'b', 'b', 'b']),
            (('post', 'mtype'), ['a', 'b', 'a', 'b', 'b'])]))
        pd.testing.assert_frame_equal(
            pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, 2.5]})
            .pivot_table(index='pre: mtype',
                         columns='post: mtype',
                         values=MEAN),
            pivot_table(df, 'pre', 'post', MEAN)[0])

    def test_columns_mismatch(self):
        df = pd.DataFrame(OrderedDict([
            (MEAN, [1, 2]),
            ('pre', ['a', 'b']),
            ('post', ['c', 'c'])]))

        pd.testing.assert_frame_equal(
            df.pivot_table(index='pre', columns='post', values=MEAN),
            pivot_table(df, 'pre', 'post', MEAN)[0])
