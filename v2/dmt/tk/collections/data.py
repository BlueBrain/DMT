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

    def collect_subcolumns(base_df):
        """get the next level of subcolumns for each column in base_df"""
        columns = list(base_df.columns)
        subcolumns = [[] for c in columns]
        for c, col in enumerate(columns):
            has_noniter = False
            has_iter = False
            for i, v in enumerate(base_df[col]):
                if isinstance(v, Mapping):
                    for k in v.keys():
                        if k not in subcolumns[c]:
                            subcolumns[c].append(k)
                    has_iter = True
                elif (
                    isinstance(v, Iterable) and
                        (not isinstance(v, str) and not isinstance(v, set))):
                    for n, _ in enumerate(v):
                        if n not in subcolumns[c]:
                            subcolumns[c].append(n)
                    has_iter = True
                else:
                    has_noniter = True

            if (has_noniter and has_iter) and 0 not in subcolumns[c]:
                subcolumns[c].append(0)
        return columns, subcolumns

    def fill_subcolumns(columns, subcolumns, base_df):
        """
        convert columns and subcolumns into an OrderedDict
        of tuples : values representing a dataframe with multi-indexed columns
        """
        newdfdict = OrderedDict()
        for i, col in enumerate(columns):
            if len(subcolumns[i]) == 0:
                if isinstance(col, tuple):
                    newdfdict[col + ('',)] = base_df[col].values
                else:
                    newdfdict[(col, '')] = base_df[col].values
            for j, subcol in enumerate(subcolumns[i]):

                if isinstance(col, tuple):
                    key = col + (subcol, )
                else:
                    key = (col, subcol)
                values = []
                for value in base_df[col]:
                    try:
                        if isinstance(value, str):
                            raise TypeError
                        values.append(value[subcol])
                    except (IndexError, KeyError):
                        values.append(None)
                    except TypeError:
                        values.append(value if subcol == 0 else None)

                newdfdict[key] = values
        return newdfdict

    columns, subcolumns = collect_subcolumns(base_df)

    if all(len(sc) == 0 for sc in subcolumns):
        return base_df

    new_dict = fill_subcolumns(columns, subcolumns, base_df)
    return multilevel_dataframe(new_dict)
