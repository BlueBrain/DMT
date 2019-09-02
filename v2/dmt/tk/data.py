import pandas as pd
from collections import Mapping, Iterable


def parameters_to_df(parameters, rdepth=0):
    """
    given a set of parameter values return a dataframe with
    multiindexed columns for dict-like parameter values, converting
    any lists to tuples
    """
    base_df = pd.DataFrame(parameters)

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

    newdfdict = {}
    for i, l1 in enumerate(lv1):
        if len(lv2[i]) == 0:
            newdfdict[l1] = base_df[l1].values
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

    return pd.DataFrame(parameters_to_df(newdfdict, rdepth+1))
