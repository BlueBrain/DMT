"""Define a cell type that can be used to extract cell properties
for given cell type"""

from abc import ABC, abstractmethod
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter

class CellProperty(
        Field):
    """Specify the key name, value type of cell property,
    value set, and values assumed."""
    def __init__(self,
                 __type__=object,
                 __value_set__={}, #empty set means any value
                 *args, **kwargs):
        """..."""
        def __is_valid(instance, value):
            """..."""
            if __value_set__:
                if collections.check(value):
                    return all(
                        isinstance(v, __type__) and v in __value_set__
                        for v in value)
                return(
                    isinstance(value, __type__)
                    and value in __value_set__)
            if collections.check(value):
                return all(
                    isinstance(v, __type__)
                    for v in value)
            return isinstance(value, __type__)
        
        if __value_set__:
            self.__value_set__\
                = __value_set__
        super().__init__(
            __is_valid__=__is_valid,
            *args, **kwargs)
        
    @property
    def value_set(self):
        """..."""
        try:
            return self.__value_set__
        except AttributeError:
            return {}

           
class CellType(
        WithFCA):
    """Define a cell type that can be used to extract cell properties.
    """
    synapse_class\
        = CellProperty(
            __name__="synapse_class",
            __type__=str,
            __value_set__={"EXC", "INH"},
            __doc__="""Excitatory or inhibitory""")
    morph_class\
        = CellProperty(
            __name__="morph_class",
            __type__=str,
            __value_set__={"PYR", "INT"},
            __doc__="""Pyramidal or interneuron""")
    mtype\
        = CellProperty(
            __name__="mtype",
            __type__=str,
            __doc__="""One of many mtypes.""",
            __examples__=["L2_MC, L6_TPC"])
    etype\
        = CellProperty(
            __name__="etype",
            __type__=str,
            __doc__="""One of many etypes.""")
    morphology\
        = CellProperty(
            __name__="morphology",
            __type__=str,
            __doc__="""One of many morphologies.""")
        
    def __init__(self, *args, **kwargs):
        """..."""
        fields_with_value\
            = {key for key, _ in kwargs.items()
               if isinstance(
                       getattr(self.__class__, key, None),
                       Field)}
        for field in set(self.get_fields()) - fields_with_value:
            values\
                = getattr(
                    getattr(self.__class__, field),
                    "value_set")
            if values:
                kwargs[field] = values
            else:
                kwargs[field] = {} #to be interpreted as Any
        super().__init__(*args, **kwargs)

    @property
    def properties(self):
        """..."""
        return {
            key: getattr(self, key, None)
            for key in self.get_fields()}

    def issubtype(this, that):
        """Is this CellType a subtype of that CellType"""
        def equal_or_in(this_value, that_value):
            """..."""
            if collections.check(this_value):
                if collections.check(that_value):
                    if not this_value:
                        return not that_value
                    if not that_value:
                        return True
                    return all(
                        v in that_value for v in this_value)
                if not this_value:
                    return False
                if len(this_value) == 1:
                    return tuple(this_value)[0] == that_value
                return False
            if collections.check(that_value):
                if not that_value:
                    return True
                return this_value in that_value
            return this_value == that_value
        return all(
            equal_or_in(this_value, getattr(that, field))
            for field, this_value in this.properties.items())

    def issupertype(this, that):
        """Is this CellType a supertype of that CellType"""
        return that.issubtype(this)
