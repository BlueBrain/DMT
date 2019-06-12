"""
Test develop the adapter pattern.
"""

from abc import ABC, abstractmethod
from ....model import AIBase, Interface
from ....model.interface import implements
from ....model.adapter import adapts

class IntegerMathTest(AIBase):
    """
    Show how to declare Interfaces / Adapoters
    """

    class AdapterInterface(Interface):
        """
        Document the methods required by this test.
        To apply this test to a model,
        these methods should be implemented by an Adapter.
        """
        def get_addition(self, model, x, y):
            """
            Add two numbers
            """
            pass

        def get_subtraction(self, model, x, y):
            """
            Subtract two numbers
            """
            pass

    def __call__(self, model):
        """..."""
        model = self.adapted(model)
        return\
            model.get_addition(1, 2) == 3 and\
            model.get_addition(2, 1) == 3 and\
            model.get_addition(3,4) == 7 and\
            model.get_subtraction(4,3) == 1 and\
            model.get_subtraction(3, 4) == -1


class IntegerMathModelPM(ABC):
    """An ABC for a model of integer math,
    that specifies it's behavior"""

    @abstractmethod
    def plus(self, x, y):
        """add integer x to y,
        to return another integer."""
        pass

    @abstractmethod
    def minus(self, x, y):
        """subtract integer y from x,
        to return another integer."""
        pass

    @abstractmethod
    def multiply(self, x, y):
        """multiply integer x and y,
        to return another integer. """
        pass

    @abstractmethod
    def divide(self, x, y):
        """divide x by y."""
        pass


class GoodIntegerMathModel(IntegerMathModelPM):
    """A good model, that does math right."""

    @classmethod
    def plus(cls, x, y):
        return x + y

    @classmethod
    def minus(cls, x, y):
        return x - y

    @classmethod
    def multiply(cls, x, y):
        return x * y

    @classmethod
    def divide(cls, x, y):
        return x / y


class BadIntegerMathModel(IntegerMathModelPM):
    """A bad model, that does math wrong."""

    @classmethod
    def plus(cls, x, y):
        return x - y

    @classmethod
    def minus(cls, x, y):
        return x + y

    @classmethod
    def multiply(cls, x, y):
        return x / y

    @classmethod
    def divide(cls, x, y):
        return x * y


@adapts(IntegerMathModelPM)
@implements(IntegerMathTest.AdapterInterface)
class TestIntegerMathModelPMAdapter:
    """
    An Adapter for TestIntegerMathModel.
    """
    def __init__(self):
        """..."""
        pass

    @classmethod
    def get_addition(cls, model, x, y):
        return model.plus(x, y)

    @classmethod
    def get_subtraction(cls, model, x, y):
        return model.minus(x, y)

    @classmethod
    def get_multiplication(cls, model, x, y):
        return model.multiply(x, y)

    @classmethod
    def get_division(cls, model, x, y):
        return model.divide(x, y)


timpm = IntegerMathTest()


def test_good_model_one():
    """
    Test good integer math models one.
    """
    timpm.adapter = TestIntegerMathModelPMAdapter()
    assert timpm(GoodIntegerMathModel())

    assert not timpm(BadIntegerMathModel())
