"""Test and develop adapters for models and validation requirements"""

from abc import ABC, abstractmethod
from dmt.adapter import requires, implements
from dmt.validation.test_case import ValidationTestCase


class TestIntegerMath(ValidationTestCase):

    @requires
    def add(self, x, y):
        """Add two numbers x and y"""
        pass

    @requires
    def sub(self, x, y):
        """Sub two numbers x and y"""
        pass

    def __call__(self, model):
        adapted = self.get_adapted_model(model)
        return (
            'PASS' if ((adapted.add(1, 1) == 2) and (adapted.sub(2, 1) == 1))
            else 'FAIL'
        )

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

    def add(self, x, y):
        return self.model.plus(x, y)

    def sub(self, x, y):
        return self.model.minus(x, y)

timpm = TestIntegerMath(TestIntegerMathModelPMAdapter)

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

    def add(self, x, y):
        return self.model.madd(x, y)

    def sub(self, x, y):
        return self.model.msub(x, y)
        

timmod = TestIntegerMath(TestIntegerMathModelModuloAdapter)

run_test(timmod, IntegerModuloMathModel(10))
