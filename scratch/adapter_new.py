"""We do not like the current way of specifying adapter methods."""

from abc import ABC, abstractmethod
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author
from dmt.aii import adaptermethod, implementation #we will need to change this method

class IntegerMethodTest(ValidationTestCase):
    """An example to show how a validation may be written."""
    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)

    @adaptermethod
    def get_addition(self, model, x, y):
        "...."
        pass

    @adaptermethod
    def get_subtraction(self, model, x, y):
        """For a 'requiredmethod', the second argument must be
        'model' (like 'self' which must be the first argument, self being a
        ValidationTestCase instance).
        The decorator 'requiredmethod' or 'required_by_model', or
        'model_capability', or just 'required' can behave like 
        'abc.abstractmethod', or may just be an (domain-specific) alias."""
        pass

    def __call__(self, model):
        d = self.validation_data
        addition_measurement\
            = self.get_addition(model, x, y)
        subtraction_measurement\
            = self.get_subtraction(model, x, y)

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



@extends(TestIntegerMethod, for_model=IntegerMathModelPM)
class TestIntegerMathModelPMAdapter:
    """The user should need to implement only the methods in,
    without having to worry about an initializer. The decorator should
    fill in the details."""

    def get_addition(self, model, x, y):
        return model.plus(x, y)

    def get_subtraction(self, mode, x, y):
        return model.minus(x, y)


#or
@applies(validation=TestIntegerMath,
         to_model=IntegerMathModelPM)
class TestIntegerMathModelPMAdapter:

    def get_addition(self, model, x, y):
        return model.plus(x, y)

    def get_subtraction(self, mode, x, y):
        return model.minus(x, y)


#or
@adapts(model=IntegerMathModelPM, for_validation=TestIntegerMath)
class TestIntegerMathModelPMAdapter:

    def get_addition(self, model, x, y):
        return model.plus(x, y)

    def get_subtraction(self, mode, x, y):
        return model.minus(x, y)



