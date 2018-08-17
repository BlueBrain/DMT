"""According to Plone(https://docs.plone.org)
Adapters make it possible to extend the behavior of a class without modifying
the class itself.
According to Zope(http://zopecomponent.readthedocs.io/en/latest/narr.html#adapters)
Adapters are components that are computed from other components to adapt them
to some interface.

An Adapter is an implementation of an interface of a special kind.
An Interface implementation may be a stand-alone class, while an implementation
that 'adapts' another class to the Interface is an Adapter.
"""

from dmt.aii.interface import Interface
from dmt.vtk.utils.descriptor \
    import Field, document_fields, ClassAttribute, ClassAttributeMeta

                  
@document_fields
class Adapter(metaclass=ClassAttributeMeta):
    """"Base for a class that adapts another class to an Interface.

    Implementation Notes
    ----------------------------------------------------------------------------
    Setting 'metaclass = ClassAttributeMeta' will ensure that the two class
    attributes have been set by a deriving class (subclass).
    """

    __adapted_type__ = ClassAttribute(
        __name__ = "__adapted_entity__",
        __type__ = type,
        __doc__ = """The class that this Adapter adapts to an Interface."""
    )
    __implemented_interface__ = ClassAttribute(
        __name__ = "__implemented_interface__",
        __type__ = type,
        __doc__  = "Interface implemented by this Adapter class."
    )


def adapter(adapted_cls):
    """A class decorator to declare that a class adapts class 'adapted_cls'."""

    def effective(cls):
        """The effective decorator method.

        Parameters
        ------------------------------------------------------------------------
        cls :: type #that is the adapter of class 'adapted_cls'"""
        cls.__adapted_type__ = adapted_cls
        return  ClassAttributeMeta(cls.__name__, (Adapter,),
                                   {a: getattr(cls, a) for a in dir(cls)})

    return effective

def get_implemented_interface(impl):
    """Get interfaces implemented by an implementation.
    We assume that one implementation will implement one interface."""
    return getattr(impl, '__implemented_interface__', None)

def get_adapted_entity(impl):
    """Get the entity adapted by implementation 'impl'.
    We assume that one implementation will adapt one model type."""
    return get_adapted_type(impl)

def get_adapted_type(cls):
    """Get the type / class adapted by implementation 'impl'.
    We assume that one implementation will adapt one model type."""
    return getattr(cls, '__adapted_type__', None)
