from abc import ABCMeta, abstractmethod
from dmt import adapter

class AIMeta(ABCMeta):
    """A metaclass that will add an AdapterInterface."""

    def __new__(meta, name, bases, dct):
        return super(AIMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        cls.AdapterInterface = adapter.interface(cls)
        super(AIMeta, cls).__init__(name, bases, dct)


class ValidationTestCase(metaclass=AIMeta):
    """A validation test case."""
    __metaclass__ = AIMeta #for Python 2 --- irrelevant in Python 3

    def __init__(self, adapter_implementation=None):
        """
        Parameters
        ----------
        adapter_implementation :: Model -> AdaptedModel
        a callable that returns an adapted model."""

        self.get_adapted_model = adapter_implementation


    @abstractmethod
    def __call__(self, model):
        """A ValidationTestCase is a callable."""
        pass
