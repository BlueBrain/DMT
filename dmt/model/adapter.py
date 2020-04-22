# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Adapt a model to an interface.
An analysis/validation will measure phenomena on a model.
A model can be adapted for an analysis/validation's requirements by
implementing methods computing these measurements.
"""
from abc import  ABC
import functools
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
    @functools.wraps(model)
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
