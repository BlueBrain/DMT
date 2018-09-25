"""Extensions to Pandas."""
import pandas as pd
from dmt.vtk.utils.logging import Logger

logger = Logger("Pandas Utilities") #we can use enviroment variables to set a file name for logging

def flatten(dataframes, keys=None, names=None):
    """Flatten a collection of Pandas DataFrames"""
    if isinstance(dataframes, dict):
        keys = list(dataframes.keys())
        return flatten([dataframes[k] for k in keys], keys=keys, names=names)
    names = [names] if not isinstance(names, list) else names
    return pd.concat(dataframes, keys=keys, names=names)

def level_values(dataframe, level):
    """Get values of given level from a dataframe."""
    index = dataframe.index
    if isinstance(index, pd.MultiIndex):
        if level not in index.names:
            raise ValueError("{} not in dataframe levels: {}"\
                             .format(level, index.names))
            
        return list(index.levels[index.names.index(level)])

    assert(isinstance(index, pd.Index))
    if level != index.name:
        raise ValueError("{} is not equal to dataframe level {}"\
                         .format(level, index.name))
    return list(index)


def ordered_values(order, values):
    """Values ordered by 'order'.

    Parameters
    ----------------------------------------------------------------------------
    order :: dict #establishing an order on values
    values :: Iterable #of values to be ordered
    """
    df = pd.DataFrame(dict(values=values, order=[order[v] for v in values]))
    return type(values)(df.sort_values(by="order")["values"])
    
def sorted(dataframe, order, level=None, ascending=True):
    """DataFrame sorted by order.

    Parameters
    ----------------------------------------------------------------------------
    dataframe :: pandas.DataFrame
    order :: lambda function #mapping values to integers (their order)
    """
    index = dataframe.index
    if isinstance(index, pd.MultiIndex):
        assert(level is not None)
        assert(level in index.names)
        keys = ordered_values(order, level_values(dataframe, level))
        return pd.concat([dataframe.xs(k, level=level) for k in keys],
                         keys=keys, names=[level])
    
    if isinstance(index, pd.Index):
        assert(not level or index.name == level)
        cols = dataframe.columns
        dataframe["order"] = [order(i) for i in index]
        return dataframe.sort_values(by="order")[cols]

    logger.warning("""sorted(...) :: DataFrame index {} is neither pandas.Index
    or pandas.MultiIndex. Returning unsorted.""".format(type(index)))
    return dataframe

