"""utility functions shared by some plotters"""
import pandas as pd
from collections import Mapping, OrderedDict


# TODO: test
def make_hashable(df, columnlabel):
    """
    take a column of dicts in a dataframe and turn them
    into a hashable column of strings. Assumes that all
    dicts in the column have the same keys
    TODO: drop that assumption

    Arguments:
        df : a dataframe
        columnlabel : the label of the column to make hashable

    Returns:
        a new dataframe with the column of columnlabel
        replaced with a new column representing all values
        of the dataframe
    """
    subdf = df[columnlabel]

    if not isinstance(subdf, pd.DataFrame):
        return df.copy(), columnlabel

    if isinstance(subdf.columns[0], tuple):
        group_description = default_group_desc_deep
    else:
        group_description = default_group_desc_shallow

    cat_column_label = (
        group_description(_row_to_dict(subdf), columnlabel))
    column_values = [default_group_label(r)
                     for i, r in subdf.iterrows()]
    return df.drop(columns=columnlabel).assign(
        **{cat_column_label: column_values}), cat_column_label


def _row_to_dict(row):

    if not isinstance(row.keys()[0], tuple):
        return OrderedDict(row.items())

    topkeys = [k[0] for k in row.keys()]
    return OrderedDict(((k, _row_to_dict(row[k])) for k in topkeys))


def default_group_desc_deep(group_dict, toplabel):
    keys = group_dict.keys()
    pre = ": {" if len(keys) > 1 else ": "
    post = "}" if len(keys) > 1 else ""
    return toplabel + pre +\
        ", ".join([default_group_desc_deep(group_dict[k], k)
                   if isinstance(group_dict[k], Mapping) else str(k)
                   for k in keys]) + post


def default_group_desc_shallow(group_dict, toplabel):
    return toplabel + ": " +\
        ", ".join([default_group_desc_shallow(group_dict[k], k)
                   if isinstance(group_dict[k], Mapping) else str(k)
                   for k in group_dict.keys()])


def default_group_label(row):
    return ", ".join(str(v) if v is not None else "_" for v in row)
