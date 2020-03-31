# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

import pandas as pd
import pandas.testing as pdt
from dmt.tk.enum import MEAN, STD
from collections import OrderedDict
from dmt.tk.plotting.utils import collapse_dataframe_column, pivot_table


def assert_odicts_of_pd_equal(d1, d2):
    """assert that two OrderedDicts with pandas series as values are equal"""
    try:
        assert d1.keys() == d2.keys()
        for v1, v2 in zip(d1.values(), d2.values()):
            pdt.assert_series_equal(v1, v2)
    except AssertionError as ae:
        print(d1.keys(), "\n", d2.keys())
        print(d1.values(), "\n\n\n", d2.values())
        raise ae


# TODO: handle lists differently by default: represent as '[<elements>]'
class Test_collapse_dataframe_column:

    def test_given_strings(self):
        """
        when there is nothing to collapse, return a copy of the column
        and a simple value-row mapping for groups
        """
        tdf = pd.DataFrame(dict(pre=['a', 'b', 'c', 'd']))
        coldf, groups = collapse_dataframe_column(tdf,  'pre')
        pd.testing.assert_frame_equal(coldf, tdf)
        assert coldf.columns[0] == 'pre'
        groups == OrderedDict([(value, value) for value in tdf.pre])

    def test_2_level_columns(self):
        """
        test collapsing a column two layers deep
        should combine the labels and values of the subcolumn
        """
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
            OrderedDict((v, tdf['pre'].iloc[i])
                        for i, v in enumerate(edf[edf.columns[0]])))

    def test_mismatched_columns(self):
        """
        when there are Nones or NaNs in the table, default behavior should be
        to place '_' as the value in the collapsed dataframe
        """
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
            groups, OrderedDict((v, tdf['buh'].iloc[i])
                                for i, v in enumerate(edf[edf.columns[0]])))

    def test_deeper(self):
        """
        test that this works up to at least three layers deep
        for deeper dataframes we need to use braces to indicate
        which sub-columns belong where
        """
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
            groups, OrderedDict((v, tdf['a'].iloc[i])
                                for i, v in enumerate(edf[edf.columns[0]])))


class Test_pivot_table:
    """
    the second and third outputs of this function are
    already tested by collapse_dataframe_column
    TODO: what is the best way to test in such a situation
    """

    def test_basic(self):
        """test the returned table for simple input"""
        df =\
            pd.DataFrame(OrderedDict([
                (MEAN, [1, 2, 1, 2]),
                ('pre', ['a', 'a', 'b', 'b']),
                ('post', ['a', 'b', 'a', 'b'])]))
        table = pivot_table(df, 'pre', 'post', MEAN)[0]
        pd.testing.assert_frame_equal(
            table,
            df.pivot_table(index='pre', columns='post',
                           values=MEAN))

    def test_2_level_columns(self):
        """
        test handling of multilevel dataframes
        the 'index' and 'columns' columns should be collapsed as necessary"""
        df = pd.DataFrame(OrderedDict([
            ((MEAN, ''), [1, 2, 1, 2]),
            ((STD, ''), [1, 2, 3, 1]),
            (('pre', 'mtype'), ['a', 'a', 'b', 'b']),
            (('post', 'mtype'), ['a', 'b', 'a', 'b'])]))
        table = pivot_table(df, 'pre', 'post', MEAN)[0]
        edf =\
            pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, 2]})\
              .pivot_table(
                  index='pre: mtype',
                  columns='post: mtype',
                  values=MEAN)
        print(table, "\n\n", edf)
        pd.testing.assert_frame_equal(
            table, edf)

    def test_duplicate_pathways(self):
        """
        when pathways are duplicated, take their mean as pandas does by default
        """
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
        """
        both columns do not need to contain the same values
        """
        df = pd.DataFrame(OrderedDict([
            (MEAN, [1, 2]),
            ('pre', ['a', 'b']),
            ('post', ['c', 'c'])]))

        pd.testing.assert_frame_equal(
            df.pivot_table(index='pre', columns='post', values=MEAN),
            pivot_table(df, 'pre', 'post', MEAN)[0])
