"""We do not like the current way of specifying adapter methods."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.aii import AdapterInterfaceBase
from dmt.aii.interface import Interface, implementation
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author

class TestIntegerMath(ValidationTestCase):
    """An example showing how to write a ValidationTestCase.
    """
    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)

    class AdapterInterface(Interface):
        """Specify all the methods you require from your adapter here. In order
        to use this validation test case, the user will have to program an
        adapter for their model. The adapter must satisfy all the requirements
        specified in this interface.

        Methods and attributes defined in the body of an interface will be
        considered abstract --- only their __doc__ string will be kept. There
        is no need to mark these attributes and methods with a decorator.
        """
        def get_addition(self, model, x, y):
            """Add x and y.

            Parameters
            --------------------------------------------------------------------
            x :: int
            y :: int

            Return
            --------------------------------------------------------------------
            int
            """
            pass

        def get_subtraction(self, model, x, y):
            """Subtract x and y.

            Parameters
            --------------------------------------------------------------------
            x :: int
            y :: int

            Return
            --------------------------------------------------------------------
            int
            """
            pass

    def __call__(self, model):
        """Makes this ValidationTestCase callable.
        Each ValidationTestCase must implement a '__call__' method.

        Parameters
        ------------------------------------------------------------------------
        model :: To be validated.
        """
        d = self.validation_data
        addition_measurement\
            = self.adapter.get_addition(model, d.x, d.y)
        subtraction_measurement\
            = self.adapter.get_addition(model, d.x, d.y)
        return ('PASS' if (all(addition_measurement == d.z) and
                           all(subtraction_measurement == d.w))
                else 'FAIL')



print("Validation TestIntegerMath authored by ", TestIntegerMath.author)
   
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


@implementation(TestIntegerMath.AdapterInterface,
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
timpm = TestIntegerMath(validation_data=test_data)
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


@implementation(TestIntegerMath.AdapterInterface, IntegerModuloMathModel)
class TestIntegerMathModelModuloAdapter:
    """Adapt IntegerModuloMathModel for TestIntegerMath."""
    @classmethod
    def get_addition(cls, model, x, y):
        return model.madd(x, y)

    @classmethod
    def get_subtraction(cls, model, x, y):
        return model.msub(x, y)

timmodulo = TestIntegerMath(validation_data=test_data,
                            adapter=TestIntegerMathModelModuloAdapter())

run_test(timmodulo, IntegerModuloMathModel(1))
