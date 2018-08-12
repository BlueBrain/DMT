"""These are ideas based on what I have been reading about the adapter pattern."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.aii import AdapterInterfaceBase, adaptermethod, implementation
from dmt.validation.test_case import ValidationTestCase

class IntegerMathTest(ValidationTestCase,
                      AdapterInterfaceBase):
    """To show semantics to declare interfaces/adapters."""

    @adaptermethod
    def get_addition(self, model, x, y):
        "add two numbers"
        pass

    @adaptermethod
    def get_subtraction(self, model, x, y):
        """subtract two numbers"""
        pass

    def __call__(self, model):
        "...call me..."
        d = self.validation_data
        model = self.AdaptedModel(model)
        #model = self.get_adapted(model)
        addition = model.get_addition(d.x, d.y)
        subtraction = model.get_subtraction(d.x, d.y)

        return ('PASS' if (all(addition == d.z) and
                           all(subtraction == d.w))
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

@implementation(IntegerMathTest.AdapterInterface,
                adapted_entity=IntegerMathModelPM)
class TestIntegerMathModelPMAdapter:
    """An adapter for TestIntegerMathModel.
    Methods in the Adapter are all class method.
    So you can instantiate with TestIntegerMathModelPMAdapter().

    Also, this examplifies that we should use an interface for the model, if
    available. Instead of two implementations of IntegerMathModelPM, we say
    that this implementation implements their interface IntegerMathModelPM."""

    def __init__(self):
        """TestIntegerMathModelPMAdapter does not need any initialization
        parameters."""
        pass

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

#model adapter need not be an input 
timpm = IntegerMathTest(validation_data=test_data)
#in which case,
#you have to set a ValidationTestCase's adapter instance
timpm.adapter = TestIntegerMathModelPMAdapter()

def run_test(tst, obj):
    result = tst(obj)
    if result == 'FAIL':
        print("FAILED: {} failed {}"\
              .format(obj.__class__.__name__, tst.__class__.__name__))
    if result == 'PASS':
        print("PASSED: {} passed {}"\
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


@implementation(IntegerMathTest.AdapterInterface, IntegerModuloMathModel)
class TestIntegerMathModelModuloAdapter:
    """Adapt IntegerModuloMathModel for TestIntegerMath."""
    @classmethod
    def get_addition(cls, model, x, y):
        return model.madd(x, y)

    @classmethod
    def get_subtraction(cls, model, x, y):
        return model.msub(x, y)

timmodulo = IntegerMathTest(validation_data=test_data,
                            adapter=TestIntegerMathModelModuloAdapter())

run_test(timmodulo, IntegerModuloMathModel(1))
