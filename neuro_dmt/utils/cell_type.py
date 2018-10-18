"""Define a cell type that can be used to extract cell properties
for given cell type"""

from abc import ABC, abstractmethod
from functools import reduce
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

class emset(set):
    """Behaves like a set that cannot be empty.
    Instead empty set is treated like the universal set."""
    elem_type = Field(
        __name__="elem_type",
        __type__=type,
        __doc__="""Type of set elements.""")
    def __init__(self,
            arg0,
            *args,
            **kwargs):
        """..."""
        if isinstance(arg0, type):
            self.elem_type = arg0
            elements\
                = (element for element in args
                   if isinstance(element, self.elem_type))
        else:
            elements = (arg0,) + args
            self.elem_type\
                = self.common_type(
                    *tuple(
                        type(element) for element in elements))
        super().__init__(elements)

    @staticmethod
    def common_type(type0, *types):
        """An attempt to find the most common recent ancestor
        (MRCA) among a sequnce of types. We use the type MROs
        to find their MRCA. We assume that all types are on a
        type inheritance tree. So situations like two types with
        MRO (T1, T2, T3, object) and (T0, T1, T2, object)
        will not occur. On an inheritance tree, the MRO of a type
        is a path of types going back to 'object'. If T1 is preceded
        by (T2, T3, object), a type T0 deriving from T1 will always
        be preceded by the entire MRO of T1 as in
        (T0, T1, T2, T3, object)"""
        types = (type0,) + types
        def common_mro(mro_shorter, mro_longer):
            """..."""
            if len(mro_shorter) > len(mro_longer):
                return common_mro(mro_longer, mro_shorter)
            if not mro_shorter or not mro_longer:
                return ()
            if mro_shorter[0] == mro_longer[0]:
                return(
                    (mro_shorter[0],) +
                    common_mro(mro_shorter[1:], mro_longer[1:]))
            return common_mro(mro_shorter, mro_longer[1:])

        mro\
            = reduce(
                common_mro,
                (_type.__mro__ for _type in types))
        return mro[0]

    def __contains__(self, x):
        """..."""
        if not self:
            return isinstance(x, self.elem_type)
        return super().__contains__(x)


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
