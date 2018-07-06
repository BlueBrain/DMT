from abc import ABC, abstractmethod
from dmt import adapter

class TestCase:
    """A validation test case."""

    def __init__(self, adapter_implementation=None):
        """
        Parameters
        ----------
        adapter_implementation :: Model -> AdaptedModel
        a callable that returns an adapted model."""

        self.get_adapted_model = adapter_implementation
        cls = self.__class__
        cls.AdapterInterface = adapter.get_adapter_interface(cls)
