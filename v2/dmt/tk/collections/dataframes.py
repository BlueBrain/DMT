import pandas as pd
from frozendict import FrozenOrderedDict
# TODO: tests. we can use the previous ones as a base, but it needs
#       to be split into sub-tests and check more levels of hashableness

# TODO: if FODict is to be public (probably shouldn't be...)
#       it should be located elsewhere
#       if we leave it here, it should be _FODict
class FODict(FrozenOrderedDict, dict):
    """
    A FrozenOrderedDict that subclasses from dict
    for pandas pretty-print compatibility
    """
    pass


def make_hashable(value):
    """
    if value is not hashable, return a hashable version

    Arguments:
        value: either Hashable, Iterable, or a Mapping
               if iterable or mapping, all elements must
               be either hashable, iterable or mapping

    Returns:
        a FODict if value is a Mapping, a tuple if it is an Iterable
    """
    from collections import Iterable, Mapping
    try:
        hash(value)
        return value
    except TypeError:
        if isinstance(value, Mapping):
            return FODict(
                (k, make_hashable(v)) for k, v in value.items())
        elif isinstance(value, Iterable):
            return (tuple(make_hashable(v) for v in value))
        else:
            raise TypeError(
                """
                {} object is neither hashable, mapping, or iterable:
                """ .format(value))


# TODO: test to ensure column order is preserved
def make_dataframe_hashable(dataframe):
    from collections import OrderedDict
    return pd.DataFrame(OrderedDict(
        (colname, make_hashable(dataframe[colname]))
        for colname in dataframe.columns))
