"""Define a cell type that can be used to extract cell properties
for given cell type"""

from abc import ABC, abstractmethod
from functools import reduce
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.collections.emuset import emuset
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

        self.property_type = __type__
        if __value_set__:
            self.__value_set__\
                = emuset(*__value_set__)
        super().__init__(
            __is_valid__=__is_valid,
        *args, **kwargs)

    def __set__(self, instance, value):
        """set value to value if set else make a set"""
        self.assert_validity(instance, value)
        if collections.check(value):
            setattr(
                instance,
                self.instance_storage_name,
                emuset(*value) if value else emuset(self.property_type)) 
            return
        setattr(
            instance,
            self.instance_storage_name,
            emuset(value))
        return
        
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
        for field_name in set(self.get_fields()) - fields_with_value:
            field\
                = getattr(
                    self.__class__,
                    field_name)
            value_set\
                = getattr(
                    field,
                    "value_set")
            if value_set:
                kwargs[field_name]\
                    = emuset(*value_set)
            else:
                kwargs[field_name]\
                    = emuset(
                        field.property_type) #to be interpreted as Any
        super().__init__(*args, **kwargs)

    @property
    def properties(self):
        """..."""
        return {
            key: getattr(self, key, None)
            for key in self.get_fields()}

    def issubtype(this, that):
        """Is this CellType a subtype of that CellType"""
        return all(
            this_field_value.issubset(getattr(that, field))
            for field, this_field_value in this.properties.items())

    def issupertype(this, that):
        """Is this CellType a supertype of that CellType"""
        return that.issubtype(this)

    def __repr__(self):
        """show me"""
        def __repr_field(field_name):
            """..."""
            self_field_value\
                = getattr(self, field_name)
            if self_field_value:
                return(
                    "{" +
                    reduce(
                        lambda acc, elem: acc + ", {}".format(elem),
                        list(self_field_value))
                    + "}")
            return "{" + "any {}".format(
                self_field_value.elem_type.__name__) + "}"

        return reduce(
            lambda accumulator, field_name: "{}\n{}".format(
                accumulator,
                "\t{}: {}".format(
                    field_name,
                    __repr_field(field_name))),
            self.get_fields(),
            "CellType:")

    def __str__(self):
        """Another way to show me?"""
        return self.__repr__()
            
#cannot do this inside class definition:
CellType.Any = CellType()


