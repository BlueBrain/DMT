from abc import ABC, abstractmethod
from dmt import adapter

class AIMeta(type):
    """A metaclass that will introspectively add an AdapterInterface."""

    def __new__(meta, name, bases, dct):
        return super(AIMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        cls.AdapterInterface = adapter.get_adapter_interface(cls)
        super(AIMeta, cls).__init__(name, bases, dct)


class ValidationTestCase(object, metaclass=AIMeta):
    """A validation test case."""
    __metaclass__ = AIMeta #for Python 2 --- no effect in Python 3

    def __init__(self, adapter_implementation=None):
        """
        Parameters
        ----------
        adapter_implementation :: Model -> AdaptedModel
        a callable that returns an adapted model."""

        self.get_adapted_model = adapter_implementation
        cls = self.__class__
        cls.AdapterInterface = adapter.get_adapter_interface(cls)
