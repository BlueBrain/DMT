"""Test Adapter & Interface without decorators."""
from abc import ABC, abstractmethod
import pandas as pd
from dmt.validation.test_case import ValidationTestCase
from dmt.model import adaptermethod
from dmt.vtk.author import Author


class IntegerMathTest(ValidationTestCase):
    """Test integer math."""

    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)
    @adaptermethod
    def get_addition(model, x, y):
        """get addition of x and y."""
        pass

    @adaptermethod
    def get_subtraction(model, x, y):
        """get subtraction of x and y"""
        pass

    def data_description(self):
        """Describe validation data."""
        return """A data frame with columns x, y, z, and w.
        Column z = x + y, w = x - y."""

    def __call__(self, model):
        """...Call Me..."""
        d = self.validation_data
        try: 
            is_pass\
                = (all(self.adapter.get_addition(model, d.x, d.y) == d.z) and
                   all(self.adapter.get_subtraction(model, d.x, d.y) == d.w))
            return 'PASS' if is_pass else 'FAIL'
        except:
            return 'INCONCLUSIVE'


   
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
