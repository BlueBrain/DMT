import pandas as pd
from collections import Mapping, Iterable


def parameters_to_df(parameters):
    """
    given a set of parameter values return a dataframe with
    multiindexed columns for dict-like parameter values, converting
    any lists to tuples
    """
    base_df = pd.DataFrame(parameters)
    lv1 = list(base_df.columns)
    lv2 = [[] for c in lv1]
    for c, col in enumerate(lv1):
        for i, v in enumerate(base_df[col]):
            if isinstance(v, Mapping):
                for k in v.keys():
                    if k not in lv2[c]:
                        lv2[c].append(k)
            elif isinstance(v, Iterable) and not isinstance(v, str):
                for n, _ in enumerate(v):
                    if n not in lv2[c]:
                        lv2[c].append(n)

    newdfdict = {}
    for i, l1 in enumerate(lv1):
        if len(lv2[i]) == 0:
            newdfdict[l1] = base_df[l1].values
        for j, l2 in enumerate(lv2[i]):
            key = (l1, l2)
            values = []
            for value in base_df[l1]:
                try:
                    values.append(value[l2])
                except (IndexError, KeyError):
                    values.append(None)
                except TypeError:
                    values.append(value if j == 0 else None)

            newdfdict[key] = values

    return pd.DataFrame(newdfdict)
