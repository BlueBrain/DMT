import pandas as pd
from dmt.tk.enum import MEAN, STD
from collections import OrderedDict
from dmt.tk.plotting.utils import collapse_dataframe_column, pivot_table


# TODO: dicts and strings
class Test_collapse_dataframe_column:

    def test_given_strings(self):
        tdf = pd.DataFrame(dict(pre=['a', 'b', 'c', 'd']))
        df, label = collapse_dataframe_column(tdf,  'pre')
        pd.testing.assert_frame_equal(df, tdf)
        assert label == 'pre'

    def test_given_dicts(self):
        tdf = pd.DataFrame(OrderedDict(
            [(('pre', 'layer'), range(4)),
             (('pre', 'mtype'), ['a', 'b', 'c', 'd'])]))
        df, label = collapse_dataframe_column(tdf,  'pre')

        edf = pd.DataFrame({('pre: layer, mtype', ''):
                            [str(l) + ", " + str(m)
                             for l, m in enumerate(['a', 'b', 'c', 'd'])]})
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
        assert label == 'pre: layer, mtype'

    def test_mismatched_dicts(self):
        tdf = pd.DataFrame(OrderedDict([
            (('buh', 'layer'), ['1', '3', '2', '3']),
            (('buh', 'mtype'), ['a', None, 'b', 'c']),
            (('buh', 'unecessary'), [None, None, None, 'detail'])]))

        edf = pd.DataFrame({
            ('buh: layer, mtype, unecessary', ''): [
                '1, a, _',
                '3, _, _',
                '2, b, _',
                '3, c, detail']})
        df, label = collapse_dataframe_column(tdf, 'buh')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)

    def test_deeper(self):
        tdf = pd.DataFrame(OrderedDict([
            (('a', 'b', 'c'), [1, 2, 3]),
            (('a', 'b', 'd'), [1, 3, 4]),
            (('a', 'c', 'g'), [2, 3, 4])]))
        edf = pd.DataFrame({
            ('a: {b: {c, d}, c: g}', '', ''):
            ['1, 1, 2', '2, 3, 3', '3, 4, 4']})
        df, label = collapse_dataframe_column(tdf, 'a')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)


class Test_prepare_plot:

    # edge cases to do
    # TODO: columns mismatch
    # TODO: duplicate pathways
    # TODO: no MEAN
    # TODO: more than two non-data columns
    def test_basic(self):
        df = pd.DataFrame(OrderedDict([
            (MEAN, [1, 2, 1, 2]),
            ('pre', ['a', 'a', 'b', 'b']),
            ('post', ['a', 'b', 'a', 'b'])]))
        table = pivot_table(df, 'pre', 'post', MEAN)
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
        table = pivot_table(df, 'pre', 'post', MEAN)
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
            pivot_table(df, 'pre', 'post', MEAN))

    def test_columns_mismatch(self):
        df = pd.DataFrame(OrderedDict([
            (MEAN, [1, 2]),
            ('pre', ['a', 'b']),
            ('post', ['c', 'c'])]))

        pd.testing.assert_frame_equal(
            df.pivot_table(index='pre', columns='post', values=MEAN),
            pivot_table(df, 'pre', 'post', MEAN))
