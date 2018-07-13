"""Test and develop adapters for models and validation requirements"""

from abc import ABC, abstractmethod
import pandas as pd
from dmt import adapter
from dmt.validation.test_case import ValidationTestCase

       
class TestIntegerMath(ValidationTestCase):
    """Preferred way to write a ValidationTestCase.
    Provide validation logic in __call__ .
    Mark all measurements desired from the model
    by decorator '@adapter.requires'."""

    @adapter.requires
    def get_addition(self, model, x, y):
        """get addition of x and y"""
        pass

    @adapter.requires
    def get_subtraction(self, model, x, y):
        """get subtraction of x and y"""
        pass

    def __call__(self, model, other_data=None):
        """Method that each ValidationTestCase must implement.
        Parameters
        ----------
        @model :: The model that needs to be validated (not adapted model).
        The model adapter provided in the definition of this test case will
        be used internally. The author of this validation does not have to
        adapt her model."""
        d = other_data if other_data else self._data
        return (
            'PASS' if (all(self.get_addition(model, d.x, d.y) == d.z) and
                       all(self.get_subtraction(model, d.x, d.y) == d.w))
            else 'FAIL'
        )
        

class TestIntegerMath0(ValidationTestCase):
    """An alternate way to write an application.
    Notice that you need to decorate __call__ with @adapted,
    so that you can pretend that the model being validated
    has the required methods defined for it. """
    @adapter.requires
    def get_addition(model, x, y):
        """get addition of x and y."""
        pass

    @adapter.requires
    def get_subtraction(model, x, y):
        """get difference x - y"""
        pass

    @adapter.adapted
    def __call__(self, model, other_data=None):
        """model should be of the type that this ValidationTestCase's
        AdapterInterface's implementation adapts."""
        d = other_data if other_data else self._data
        return (
            'PASS' if (all(model.get_addition(d.x, d.y) == d.z) and
                       all(model.get_subtraction(d.x, d.y) == d.w))
            else 'FAIL'
        )


test_data = pd.DataFrame(dict(
    x=[1, 2, 3, 4, 5, 6, 7],
    y=[1, 2, 3, 4, 3, 2, 1],
    z=[2, 4, 6, 8, 8, 8, 8],
    w=[0, 0, 0, 0, 2, 4, 6]
))


class IntegerMathModelPM(ABC):
    """An ABC for a model of integer math,
    that specifies its behavior."""

    @abstractmethod
    def plus(self, x, y):
        """add integer y to y,
        to return another integer."""
        pass

    @abstractmethod
    def minus(self, x, y):
        """subtract integer y from x,
        to return another integer."""
        pass


class BadIntegerMathModel(IntegerMathModelPM):

    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x + y


class GoodIntegerMathModel(IntegerMathModelPM):

    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x - y


@adapter.implementation(TestIntegerMath.AdapterInterface)
class TestIntegerMathModelPMAdapter:

    def __init__(self, model):
        self.model = model

    def get_addition(self, x, y):
        """implementation of the required method get_addition"""
        return self.model.plus(x, y)

    def get_subtraction(self, x, y):
        """implementation of the required method get_subtraction"""
        return self.model.minus(x, y)


timpm = TestIntegerMath(test_data, TestIntegerMathModelPMAdapter)

def run_test(tst, obj):
    result = tst(obj)
    if result == 'FAIL':
        print("FAILED: {}".format(obj.__class__.__name__))
    if result == 'PASS':
        print("PASSED: {}".format(obj.__class__.__name__))

run_test(timpm, BadIntegerMathModel())

run_test(timpm, GoodIntegerMathModel())


class IntegerModuloMathModel:
    """Modulo math."""
    def __init__(self, n):
        self.__n = n

    def madd(self, x, y):
        return (x + y) % self.__n

    def msub(self, x, y):
        return (x - y) % self.__n


@adapter.implementation(TestIntegerMath.AdapterInterface)
class TestIntegerMathModelModuloAdapter:

    def __init__(self, model):
        self.model = model

    def get_addition(self, x, y):
        return self.model.madd(x, y)

    def get_subtraction(self, x, y):
        return self.model.msub(x, y)
        

timmod = TestIntegerMath(test_data, TestIntegerMathModelModuloAdapter)

run_test(timmod, IntegerModuloMathModel(10))
