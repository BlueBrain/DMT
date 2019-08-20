"""utility functions shared by some plotters"""


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
    dict_column = df[columnlabel]

    if not isinstance(dict_column[0], dict):
        return df.copy(), columnlabel

    # get all of the unique keys of dicts in the column, sorted
    keys = sorted(set(k for cvalue in dict_column for k in cvalue.keys()))
    cat_column_label = columnlabel + ": " + ", ".join(keys)
    column_values = [", ".join(str(d.get(key, "_"))
                               for key in keys)
                     for d in dict_column.values]
    return df.drop(columns=columnlabel).assign(
        **{cat_column_label: column_values}), cat_column_label
