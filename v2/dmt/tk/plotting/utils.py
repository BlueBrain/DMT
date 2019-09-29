"""utility functions shared by some plotters"""
import pandas as pd
from collections import Mapping, OrderedDict


def default_group_label(row):
    if not isinstance(row, pd.Series):
        return row
    return ", ".join(str(v) if v is not None else "_" for v in row.values)


# TODO: test
def collapse_dataframe_column(df, columnlabel,
                              value_callback=default_group_label):
    """
    take a dataframe with potentially multiindexed columns
    and collapse a column to a single-string representation

    Arguments:
        df : a dataframe
        columnlabel : the label of the column to make hashable
        value_callback : the callback used to produce collapsed values
                         for each row in df
    Returns:
        a new dataframe consisting of the collapsed column
        an OrderedDict mapping collapsed values onto the original rows they
        represent
    """
    subdf = df[[columnlabel]]

    cat_column_label = columnlabel
        #_default_group_desc(subdf, ''))
    column_values = [value_callback(r)
                     for i, r in subdf.iterrows()]
    if isinstance(subdf[columnlabel], pd.Series):
        iterator = subdf[columnlabel].iteritems()
    else:
        iterator = subdf[columnlabel].iterrows()

    groups = OrderedDict([(column_values[i], r)
                          for i, r in iterator])
    return pd.DataFrame({cat_column_label: column_values}), groups


# TODO: ugly default, refactor
def _default_group_desc(df, st):

    def _row_to_dict(row):
        if not isinstance(row.keys()[0], tuple):
            return OrderedDict(row.items())

        topkeys = [k[0] for k in row.keys()]
        return OrderedDict(((k, _row_to_dict(row[k])) for k in topkeys))

    def _default_group_desc_deep(group_dict, toplabel):
        keys = group_dict.keys()
        pre = ": {" if len(keys) > 1 else ": "
        post = "}" if len(keys) > 1 else ""
        return str(toplabel) + pre +\
            ", ".join([_default_group_desc_deep(group_dict[k], k)
                       if isinstance(group_dict[k], Mapping) else str(k)
                       for k in keys]) + post

    def _default_group_desc_shallow(group_dict, toplabel):
        return str(toplabel) + ": " +\
            ", ".join([_default_group_desc_shallow(group_dict[k], k)
                       if isinstance(group_dict[k], Mapping) else str(k)
                       for k in group_dict.keys()])

    if isinstance(df.columns[0], tuple):
        first = df.columns[0][0]
        if len(df.columns[0]) == 2:
            return _default_group_desc_shallow(_row_to_dict(df[first]), first)
        else:
            return _default_group_desc_deep(_row_to_dict(df[first]), first)
    else:
        return df.columns[0]


def pivot_table(df, index, columns, values,
                value_callback=default_group_label, **kwargs):
    """
    construct a pivot table for a dataframe with potentially
    multiindexed columns

    Arguments:
        df: a pandas DataFrame, potentially with multiindexed columns
        index: str, the column of df to use for index (top-level column name)
        columns: str, the column of df to use for the columns ''
        values: the column of the df containing the values to pivot
        value_callback: a callback used to collapse the index and columns
                        columns (see collapse_dataframe_column)
        kwargs: additional arguments to pandas.DataFrame.pivot_table can be
                passed as keyword arguments

    Returns:
        piv_df: pandas dataframe with collapsed version of
                'index' column as index, collapsed version of 'columns' column
                 as the column values and values as the cell contents
        fromgrps: OrderedDict mapping collapsed values in the index column
                  to their initial state
        togrps: OrderedDict mapping collapsed values in the columns column
                to their initial state
    """
    fromdf, fromgrps = collapse_dataframe_column(
        df, index, value_callback=value_callback)
    fromcol = fromdf.columns[0]
    todf, togrps = collapse_dataframe_column(
        df, columns, value_callback=value_callback)
    tocol = todf.columns[0]
    # flatten out multiindex
    valdf = pd.DataFrame({values: df[values]})
    flat_df = pd.concat((fromdf, todf, valdf), axis=1)
    piv_df = flat_df.pivot_table(columns=tocol, index=fromcol, values=values,
                                 **kwargs)
    return piv_df, fromgrps, togrps
