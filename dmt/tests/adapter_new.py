
from abc import ABC, abstractmethod
import pandas as pd
from dmt import adapter
from dmt.validation.test_case import ValidationTestCase


class TestIntegerMath(ValidationTestCase):
    """Preferred way to write a ValidationTestCase.
    Notes for the users of this validation test case
    ------------------------------------------------
    Provide validation logic in __call__.
    Mark all measurements, or any other data, required from the
    model by decorator '@adapter.requires'."""

    @adapter.provided
    def get_addition(adapter, model, x, y):
        """get addition of x and y"""
        pass

    @adapter.provided
    def get_subtraction(adapter, model, x, y):
        """get difference of x and y"""
        pass

    def __call__(self, model, other_data=None):
        """Method that each ValidationTestCase must implement.
        Parameters
        ----------
        @model :: The model that needs to be validated (not adapted model).
        The model adapter provided in the definition of this test case will
        be used internally to define an interface. The user of this validation
        test case will have to implement the resulting adapter interface."""

        d = other_data if other_data else self.data

        addition_measurement = self.adapter.get_addition(model, d.x, d.y)
        subtraction_measurement = self.adapter.get_subtraction(model, d.x, d.y)

        return ('PASS' if (all(addition_measurement == d.z) and
                           all(subtraction_measurement == d.w))
                else 'FAIL')
   
   
#here is an example of how to use ABC's as interfaces
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

class GoodIntegerMathModel(IntegerMathModelPM):

    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x - y


class BadIntegerMathModel(IntegerMathModelPM):

    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x + y


@adapter.interface_implementation(TestIntegerMath)
class TestIntegerMathModelPMAdapter:
    @classmethod
    def get_addition(cls, model, x, y):
        return model.plus(x, y)
    @classmethod
    def get_subtraction(cls, model, x, y):
        return model.minus(x, y)


test_data = pd.DataFrame(dict(
    x=[1, 2, 3, 4, 5, 6, 7],
    y=[1, 2, 3, 4, 3, 2, 1],
    z=[2, 4, 6, 8, 8, 8, 8],
    w=[0, 0, 0, 0, 2, 4, 6]
))


timpm = TestIntegerMath(data=test_data)

def run_test(tst, obj):
    result = tst(obj)
    if result == 'FAIL':
        print("FAILED: {} failed {}"\
              .format(obj.__class__.__name__, tst.__class__.__name__))
    if result == 'PASS':
        print("PASSED: {} failed {}"\
              .format(obj.__class__.__name__, tst.__class__.__name__))

run_test(timpm, BadIntegerMathModel())

run_test(timpm, GoodIntegerMathModel())


class IntegerModuloMathModel:
    """Module math."""
    def __init__(self, n):
        self.__n = n

    def madd(self, x, y):
        return (x+y) % self.__n

    def msub(self, x, y):
        return (x - y) % self.__n


@adapter.interface_implementation(TestIntegerMath)
