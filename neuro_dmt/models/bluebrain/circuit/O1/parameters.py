"""Parameters used for measurements. """
import collections
import copy
from neuro_dmt.measurement.parameter import Column

class HyperColumn(
        Column):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        values=\
            kwargs.get(
                "values", range(7))
        super().__init__(
            value_type=str,
            values=["mc{}_Column".format(n) for n in values],
            label="$target",
            *args, **kwargs)

def transform(
        instance,
        method_name,
        mapping):
    """..."""
    modified_instance=\
        copy.deepcopy(instance)
    method=\
        getattr(instance, method_name)

    def modified_method(*args, **kwargs):
        """Modifed {}""".format(method.__doc__)
        x = method(instance, *args, **kwargs)
        if isinstance(x, collections.Iterable):
            for y in x:
                yield mapping(y)
        else:
            return mapping(x)

    setattr(
        modified_instance,
        method_name,
        modified_method)
    return\
        modified_instance
