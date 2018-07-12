"""Test and develop adapters for models and validation requirements"""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.adapter import requires, implements
from dmt.validation.test_case import ValidationTestCase

#test data


class TestIntegerMath(ValidationTestCase):

    @requires
    def get_addition(measurable_system, x, y):
        """get addition of x and y."""
        pass

    @requires
    def get_difference(measurable_system, x, y):
        """get difference x - y"""
        pass

    def __call__(self, model):
        adapted_model = self.get_adapted_model(model)

        #the author is supposed to know the format data is in.
        d = self._data
        return (
            'PASS' if (all(adapted_model.get_addition(d.x, d.y) == d.z) and
                       all(adapted_model.get_difference(d.x, d.y) == d.w))
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


@implements(TestIntegerMath.AdapterInterface)
class TestIntegerMathModelPMAdapter:

    def __init__(self, model):
        self.model = model

    def get_addition(self, x, y):
        return self.model.plus(x, y)

    def get_difference(self, x, y):
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


@implements(TestIntegerMath.AdapterInterface)
class TestIntegerMathModelModuloAdapter:

    def __init__(self, model):
        self.model = model

    def get_addition(self, x, y):
        return self.model.madd(x, y)

    def get_difference(self, x, y):
        return self.model.msub(x, y)
        

timmod = TestIntegerMath(test_data, TestIntegerMathModelModuloAdapter)

run_test(timmod, IntegerModuloMathModel(10))
