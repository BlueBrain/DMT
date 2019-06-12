"""These are ideas based on what I have been reading about the adapter pattern."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.model import interface, adapter
from dmt.model import adaptermethod
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author

class IntegerMathTest(ValidationTestCase):
    """To show semantics to declare interfaces/adapters."""

    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)

    def data_description(self):
        """Describe the data used by this validation."""
        return """A data frame with columns x, y, z, and w. Column z = x + y,
        Column w = x - y."""

    class AdapterInterface(interface.Interface):
        """You may define the interface required of an adapter  by a validation
        as a class. The result is the same as using decorator 'adaptermethod'
        before each member function required by the interface."""

        def get_addition(self, model, x, y):
            "add two numbers"
            pass

        def get_subtraction(self, model, x, y):
            """subtract two numbers"""
            pass

        def get_multiplication(self, model, x, y):
            """multiply two numbers"""
            pass
        def get_division(self, model, x, y):
            """divide two numbers"""
            pass

    def __call__(self, model):
        "...call me..."
        d = self.validation_data
        model = self.adapted(model)
        #model = self.get_adapted(model)
        addition = model.get_addition(d.x, d.y)
        subtraction = model.get_subtraction(d.x, d.y)
        multiplcation = model.get_multiplication(d.x, d.y)
        division = model.get_division(d.x, d.y)

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

    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        return x / y


class BadIntegerMathModel(IntegerMathModelPM):
    """A bad model, that does math wrong."""

    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return x + y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        return y / x


@adapter.adapter(IntegerMathModelPM)
@interface.implementation(IntegerMathTest.AdapterInterface)
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

    @classmethod
    def get_multiplication(cls, model, x, y):
        return model.multiply(x, y)

    @classmethod
    def get_division(cls, model, x, y):
        return model.divide(x, y)


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

    def mmul(self, x, y):
        return (x * y) % self.__n

    def mdiv(self, x, y):
        return (x / y) % self.__n



@adapter.adapter(IntegerModuloMathModel)
@interface.implementation(IntegerMathTest.AdapterInterface)
class TestIntegerMathModelModuloAdapter:
    """Adapt IntegerModuloMathModel for TestIntegerMath."""
    @classmethod
    def get_addition(cls, model, x, y):
        return model.madd(x, y)

    @classmethod
    def get_subtraction(cls, model, x, y):
        return model.msub(x, y)

    @classmethod
    def get_multiplication(cls, model, x, y):
        return model.mmul(x, y)

    @classmethod
    def get_division(cls, model, x, y):
        return model.mdiv(x, y)

timmodulo = IntegerMathTest(validation_data=test_data,
                            adapter=TestIntegerMathModelModuloAdapter())

run_test(timmodulo, IntegerModuloMathModel(1))
