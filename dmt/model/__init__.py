# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Classes and methods for models.
"""


from abc import ABC, ABCMeta
from types import FunctionType
from .interface import\
    interfacemethod,\
    get_interface,\
    get_implementations
from .adapter import\
    get_models_adapted
from ..tk.field import Field, WithFields
from ..tk.journal import Logger


def adaptermethod(method):
    """
    Decorator to mark a method.
    """
    method = interfacemethod(method)
    method.__doc__ = """
    Method defined as an Adapter Interface, that will need implementation in an
    Adapter.
    {}
    ---------------------------------------------------------------------------
    """.format(method.__doc__)
    return method


class AIMeta(ABCMeta):
    """
    A metaclass that will add an AdapterInterface
    """
    def __new__(mcs, name, bases, attribute_dict):
        """
        Give an AdapterInterface to class 'cls' only if it does not have one
        already.
        """
        if "AdapterInterface" not in attribute_dict:
            ainame = "{}AdapterInterface".format(name)
            adapter_interface = get_interface(attribute_dict, name=ainame)
            if adapter_interface is not None:
                attribute_dict["AdapterInterface"] = adapter_interface
            else:
                pass
        return super().__new__(
            mcs, name, bases, attribute_dict)

    def __init__(cls, name, bases, attribute_dict):
        """
        No specifics for now.
        """
        super().__init__(name, bases, attribute_dict)


class AIBase(metaclass=AIMeta):
    """
    Base for classes that will declare an adapter interface.
    """

    _adapter = None

    def __init__(self,
        *args, **kwargs):
        """..."""
        self.logger =\
            Logger(client=self.__class__.__name__)
        self._adapter =\
            kwargs.get(
                "model_adapter",
                kwargs.get(
                    "adapter",
                    None))
        if self._adapter:
            self.adapter = self._adapter #validate and assign
        super().__init__(
            *args, **kwargs)

    @property
    def adapter(self):
        """
        Another name for model_adapter.
        """
        if self._adapter is None:
            raise AttributeError(
                """
                Adapter not set for {}.
                """.format(self.__class__.__name__))
        return self._adapter

    @adapter.setter
    def adapter(self, value):
        """
        Reset the adapter, after validating the new 'value'
        """
        if value is None or self.AdapterInterface.is_implemented_by(value):
            self._adapter = value
        else:
            self.logger.suggest(
                self.logger.get_source_info(),
                self.AdapterInterface.__implementation_guide__)
            raise ValueError(
                """
                {} does not implement {}'s AdapterInterface.
                """.format(value, self.__class__.__name__))
        pass

    def unset_adapter(self):
        """
        Unset the adapter.
        """
        self.adapter = None

    @classmethod
    def accepted_models(cls):
        """
        Models that this class's AdapterInterface will accept.
        """
        adapted_models = {}
        for impl in get_implementations(cls.AdapterInterface).values():
            adapter_models.update(get_models_adapted(impl))

        return adapted_models

    def adapted(self, model):
        """
        Get an object that is an adapted model.
        """

        def __adapted_method(method):
            """..."""
            def __effective(this, *args, **kwargs):
                original = getattr(self.adapter, method)
                return original(model, *args, **kwargs)
            return __effective

        name =\
            "{}AdaptedTo{}".format(
                model.__class__.__name__,
                self.__class__.__name__)
        class_type =\
            type(
                name,
                (object,),
                {m: __adapted_method(m)
                 for m in self.AdapterInterface.__interfacemethods__})
        return class_type()


from .interface import Interface
from .adapter import Adapter
