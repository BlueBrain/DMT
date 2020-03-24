"""
Adapt a model to an interface.
An analysis/validation will measure phenomena on a model.
A model can be adapted for an analysis/validation's requirements by
implementing methods computing these measurements.
"""
from abc import  ABC
from ..tk.field import\
    ClassAttribute,\
    ClassAttributeMetaBase

class Adapter(ABC):
    """Base class for a model adapter class.
    This base class defines the protocol.
    An Adapter adapts a model by implementing an Interface for it.
    """

    __adapted_models__ = ClassAttribute(
        """
        A dict mapping name to the class representing the model
        that this Adapter adapts to an Interface. An Adapter may adapt more
        than one model.
        """)
    __implemented_interfaces__ = ClassAttribute(
        """
        Adapter Interfaces implemented by this adapter.
        """)


def adapts(model):
    """
    A class decorator to declare that a class adapts a class model.
    You may use this decorator to mark the classes that adapt models,
    instead of basing your implementation on the base class Adapter.

    Arguments
    ~   model :: A Python Class that represents the adapted model.
    """
    def decorated(adapting_class):
        """
        The effective decorator method.

        Arguments
        ~   adapting_class :: Class that adapts --- to be decorated.
        """

        try:
            adapting_class.__adapted_models__[model.__name__] = model
        except AttributeError:
            adapting_class.__adapted_models__ = {model.__name__: model}

        if not hasattr(adapting_class, "__implemented_interfaces__"):
            adapting_class.__implemented_interfaces__ = {}

        Adapter.register(adapting_class)

        return adapting_class

    return decorated


def get_interfaces_implemented(model_adapter):
    """
    Get interfaces implemented by Adapter.
    """
    return getattr(model_adapter,  "__implemented_interfaces__", None)

def get_models_adapted(model_adapter):
    """
    Get models adapted.
    """
    return getattr(model_adapter, "__adapted_models__", None)
