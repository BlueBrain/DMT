from abc import abstractmethod
from dmt import adapter

class ValidationTestCase(metaclass=adapter.AIMeta):
    """A validation test case."""
    __metaclass__ = adapter.AIMeta #for Python 2 --- irrelevant in Python 3

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
