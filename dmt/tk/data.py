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

import pandas as pd
from collections import Mapping, Iterable, OrderedDict


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

    lv1 = list(base_df.columns)
    lv2 = [[] for c in lv1]
    at_least_one_sub = False
    for c, col in enumerate(lv1):
        has_noniter = False
        has_iter = False
        for i, v in enumerate(base_df[col]):
            if isinstance(v, Mapping):
                for k in v.keys():
                    if k not in lv2[c]:
                        lv2[c].append(k)
                has_iter = True
                at_least_one_sub = True
            elif (
                isinstance(v, Iterable) and
                    (not isinstance(v, str) and not isinstance(v, set))):
                for n, _ in enumerate(v):
                    if n not in lv2[c]:
                        lv2[c].append(n)
                has_iter = True
                at_least_one_sub = True
            else:
                has_noniter = True

        if (has_noniter and has_iter) and 0 not in lv2[c]:
            lv2[c].append(0)

    if not at_least_one_sub:
        return base_df

    newdfdict = OrderedDict()
    for i, l1 in enumerate(lv1):
        if len(lv2[i]) == 0:
            if isinstance(l1, tuple):
                newdfdict[l1 + ('',)] = base_df[l1].values
            else:
                newdfdict[(l1, '')] = base_df[l1].values
        for j, l2 in enumerate(lv2[i]):
            if isinstance(l1, tuple):
                key = l1 + (l2, )
            else:
                key = (l1, l2)
            values = []
            for value in base_df[l1]:
                try:
                    if isinstance(value, str):
                        raise TypeError
                    values.append(value[l2])
                except (IndexError, KeyError):
                    values.append(None)
                except TypeError:
                    values.append(value if l2 == 0 else None)

            newdfdict[key] = values
    return pd.DataFrame(multilevel_dataframe(newdfdict))
