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

    # for each column, check for mappings and iterables to determine
    # which subcolumns are necessary
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

    # if there are no necessary subcolumns, just return the dict
    if not at_least_one_sub:
        return base_df

    # for every necessary subcolumn, put the appropriate values
    newdfdict = OrderedDict()
    for i, l1 in enumerate(lv1):
        if len(lv2[i]) == 0:
            # when this method recurses, it will encounter tuple column names
            if isinstance(l1, tuple):
                newdfdict[l1 + ('',)] = base_df[l1].values
            else:
                newdfdict[(l1, '')] = base_df[l1].values
        for j, l2 in enumerate(lv2[i]):
            # when this method recurses, it will encounter tuple column names
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

    # recurse to provide sub-subcolumns if needed, and so on
    return pd.DataFrame(multilevel_dataframe(newdfdict))
