"""A test for model interfaces and adapters."""
import unittest
import inspect
from dmt.interface import interface, implements

@interface
class IIntegerMath:
    """An interface that specifies the behavior of a model of integer math ."""

    @abstractmethod
    def add(a, b):
        """Add two integers"""
        pass

    @abstractmethod
    def subtract(a, b):
        """Subtract two integers"""
        pass

    @abstractmethod
    def multiply(a, b):
        """Multiply two integers"""
        pass

    @abstractmethod
    def divide(a, b):
        """Divide two integers"""
        pass

@interface
class IBadIntegerMath:
    """An interface that specifies the behavior of a model of integer math,
    but does not mark methods as abstract"""

    @abstractmethod
    def add(a, b):
        """Add two integers"""
        pass

    def subtract(a, b):
        """Subtract two integers"""
        pass

    def multiply(a, b):
        """Multiply two integers"""
        pass

    def divide(a, b):
        """Divide two integers"""
        pass


class InterfaceTest(TestCase):
    """Describes the behavior desired from an Interface metaclass,
    its implementation, and tests the actually implemented behavior using
    an interface for integer math."""

    def test(self):
        """test method"""
        self.assert(hasattr(IIntegerMath, 'implementation_guide'))

        inherited_methods = [
            n for n, _ in inspect.getmembers(
                BadIntegerMath.__base__,
                predicate=lambda m: inspect.isfunction(m)|inspect.ismember(m))
        ]

                             
        for name, member in instance.getmembers(BadIIntegerMath,
                                                predicate=inspect.isfunction)

if __name__ == '__main__':
    unittest.main()
