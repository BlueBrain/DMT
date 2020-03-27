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

"""utility functions shared by some plotters"""
import pandas as pd
from collections import Mapping, OrderedDict
from dmt.tk.terminology.data import data as dataterms


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
                     for _, r in subdf.iterrows()]
    if isinstance(subdf[columnlabel], pd.Series):
        iterator = subdf[columnlabel].iteritems()
    else:
        iterator = subdf[columnlabel].iterrows()

    groups = OrderedDict([(column_values[i], r)
                          for i, r in iterator])
    return pd.DataFrame({cat_column_label: column_values}), groups

def default_label_callback(row):
    try:
        return ", ".join(str(v) for v in row.values())
    except AttributeError as ae:
        return str(row)
    except TypeError as te:
        return ", ".join(str(v) for v in row.values)

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

def infer_index_columns(cols, index=None, columns=None):
    non_data_columns = [c for c in cols if c not in dataterms.all]
    if not len(non_data_columns) == 2:
        raise ValueError(
            "if index and columns are not both specified, "
            "dataframe must have exactly two columns aside from {}, "
            "found: {}"
            .format(dataterms.all, non_data_columns))
    if index is None and columns is None:
        return non_data_columns[0], non_data_columns[1]
    elif index is None:
        index = [c for c in non_data_columns if c != columns][0]
    elif columns is None:
        columns = [c for c in non_data_columns if c != index][0]
    return index, columns

def pivot_table(df, index=None, columns=None, values=dataterms.samples,
                label_callback=default_label_callback, **kwargs):
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
    dataframe_cols = df.columns
    if isinstance(dataframe_cols[0], tuple):
        dataframe_cols = []
        for c in df.columns:
            if c[0] not in dataframe_cols:
                dataframe_cols.append(c[0])

    if index is None or columns is None:
        index, columns = infer_index_columns(
            [c for c in dataframe_cols if c != values],
            index=index, columns=columns)

    def uniquevals(dforseries):
        if isinstance(dforseries, pd.DataFrame):
            return [v for _, v in
                    dforseries.drop_duplicates().iterrows()]
        return dforseries.unique()

    def iterthrough(dforseries):
        if isinstance(dforseries, pd.DataFrame):
            return dforseries.iterrows()
        return dforseries.iteritems()

    # TODO: handle case where two different groups
    #       produce same label
    fromgrps = OrderedDict([(label_callback(grp), grp)
                            for grp in uniquevals(df[index])])
    togrps = OrderedDict([(label_callback(grp), grp)
                          for grp in uniquevals(df[columns])])

    # flatten out multiindex
    flat_df = pd.DataFrame(OrderedDict([
        (index, [label_callback(grp) for _, grp in iterthrough(df[index])]),
        (columns, [label_callback(grp) for _, grp in iterthrough(df[columns])]),
        (values, df[values])]))

    piv_df = flat_df.pivot_table(columns=columns, index=index, values=values,
                                 **kwargs)\
                    .reindex(fromgrps.keys(), axis=0)\
                    .reindex(togrps.keys(), axis=1)
    return piv_df, fromgrps, togrps
