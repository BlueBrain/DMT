"""A test for model interfaces and adapters."""
import unittest
from dmt.model.interface import ModelInterface

class IIntegerMath(ModelInterface):
    """An interface that specifies the behavior of a model of integer math ."""
    def add(a, b):
        """Adds two integers"""
        pass
