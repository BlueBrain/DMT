# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

import six
from collections import OrderedDict
from collections.abc import Hashable, Mapping, Iterable, Generator
from frozendict import FrozenOrderedDict
import pandas as pd

def multilevel_dataframe(data_dict_s):
    """
    given a dict representing a dataframe, convert complex
    datatypes (lists, tuples, dicts) to subcolumns.
    e.g. {'a': [{'b': 0, 'c': 1}]} to

      a
     b c
     0 1

    Arguments:
        data_dict_s: a dict of lists or list of dicts representing data
                     may have iterables and mappables as entries

    Returns:
        a dataframe with any mappables converted to subcolumns where
        the subcolumn names correspond to the mappable keys, and where
        any non-string and non-set iterables are converted to subcolumns
        where the index is the column name.
    """
    base_df = pd.DataFrame(data_dict_s)

    def with_subcol(col, subcol):
        """create subcolumn name from supercolumn and subcolumn"""
        if isinstance(col, tuple):
            return col + (subcol, )
        return (col, subcol)

    def get_values(df, col, k):
        """
        check col in df for the values of subcolumn k,
        where k is absent, fill None instead
        """
        vals = []
        for v in df[col]:
            try:
                if isinstance(v, str):
                    raise TypeError
                vals.append(v[k])
            except (KeyError, IndexError):
                vals.append(None)
            except TypeError:
                # scalar values are subcolumn 0
                vals.append(v if k == 0 else None)
        return vals

    def collect_subcolumns(base_df):
        """get the next level of subcolumns for each column in base_df"""
        columns = list(base_df.columns)
        subcolumns = [[] for c in columns]
        newdfdict = OrderedDict()
        for c, col in enumerate(columns):
            has_noniter = False
            has_iter = False
            for i, v in enumerate(base_df[col]):
                if isinstance(v, Mapping):
                    for k in v.keys():
                        if k not in subcolumns[c]:
                            subcolumns[c].append(k)
                            newdfdict[with_subcol(col, k)]\
                                = get_values(base_df, col, k)
                    has_iter = True
                elif (
                    isinstance(v, Iterable) and
                        (not isinstance(v, str) and not isinstance(v, set))):
                    for n, _ in enumerate(v):
                        if n not in subcolumns[c]:
                            subcolumns[c].append(n)
                            newdfdict[with_subcol(col, n)]\
                                = get_values(base_df, col, n)
                    has_iter = True
                else:
                    has_noniter = True

            if (has_noniter and has_iter) and 0 not in subcolumns[c]:
                subcolumns[c].append(0)
                newdfdict[with_subcol(col, 0)] = get_values(base_df, col, 0)
            if not has_iter:
                newdfdict[with_subcol(col, '')] = base_df[col]

        return newdfdict, columns, subcolumns

    newdfdict, columns, subcolumns = collect_subcolumns(base_df)

    if all(len(sc) == 0 for sc in subcolumns):
        return base_df
    return multilevel_dataframe(newdfdict)


def make_hashable(values):
    """
    Make the elements of iterable `values` hashable.
    Or if `values` is a singleton, make it hashable.
    """
    def _hashable_one(value):
        """..."""
        if isinstance(value, Hashable):
            return value
        try:
            return FrozenOrderedDict(value)
        except TypeError as frozen_ordered_dict_error:
            try:
                return tuple(value)
            except TypeError as tuple_error:
                pass
        raise TypeError(
            """
            {} object is neither hashable, mapping, or iterable:
            Error when tried to create FrozenOrderedDict: {}
            Error when tried to create a tuple: {}
            """\
            .format(
                value,
                frozen_ordered_dict_error,
                tuple_error))

    def _ordered(dict_like):
        """..."""
        if isinstance(dict_like, (FrozenOrderedDict, OrderedDict)):
            return _ordered
        assert isinstance(dict_like, dict)
        return OrderedDict(
            sorted(dict_like.items(), key=lambda kv: kv[0]))

    if not isinstance(values, Iterable):
        return _hashable_one(values)
    if isinstance(values, six.string_types):
        return _hashable_one(values)
    if isinstance(values, Mapping):
        return\
            FrozenOrderedDict(
                (make_hashable(key), make_hashable(value))
                for key, value in _ordered(values).items())

    generator = (make_hashable(value) for value in values)
    if isinstance(values, Generator):
        return generator
    if isinstance(values, pd.Series):
        return pd.Series(generator)
    return tuple(generator)
