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
