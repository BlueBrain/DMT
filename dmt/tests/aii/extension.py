"""We do not like the current way of specifying adapter methods."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author
from dmt.aii import modelmethod, extends #we will need to change this method

class IntegerMathTest(ValidationTestCase):
    """An example to show how a validation may be written."""
    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)

    @modelmethod
    def get_addition(self, model, x, y):
        "...."
        pass

    @modelmethod
    def get_subtraction(self, model, x, y):
        """For a 'modelmethod', the second argument must be
        'model' (like 'self' which must be the first argument, self being a
        ValidationTestCase instance).
        The decorator 'requiredmethod' or 'required_by_model', or
        'model_capability', or just 'required' can behave like 
        'abc.abstractmethod', or may just be an (domain-specific) alias."""
        pass

    @modelmethod
    def get_multiplication(self, model, x, y):
        """multiplication of x with y"""
        pass

    @modelmethod
    def get_division(self, model, x, y):
        """division of x by y"""
        pass

    def __call__(self, model):
        d = self.validation_data
        addition_measurement\
            = self.get_addition(model, d.x, d.y)
        subtraction_measurement\
            = self.get_subtraction(model, d.x, d.y)

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



@modelextension(IntegerMathTest)
class IntegerMathModelPMTest:
    """The user should need to implement only the methods in,
    without having to worry about an initializer. The decorator should
    fill in the details."""

    def get_addition(self, model, x, y):
        return model.plus(x, y)

    def get_subtraction(self, model, x, y):
        return model.minus(x, y)

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

test_data = pd.DataFrame(dict(
    x=[1, 2, 3, 4, 5, 6, 7],
    y=[1, 2, 3, 4, 3, 2, 1],
    z=[2, 4, 6, 8, 8, 8, 8],
    w=[0, 0, 0, 0, 2, 4, 6]
))

#model adapter need not be an input 
timpm = IntegerMathModelPMTest(validation_data=test_data)
#in which case,

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

