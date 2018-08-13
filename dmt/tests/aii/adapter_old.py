from abc import ABC, abstractmethod
import pandas as pd
from dmt.aii import AdapterInterfaceBase, adaptermethod
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author


class TestIntegerMath(ValidationTestCase):
    """Preferred way to write a ValidationTestCase.
    Notes for the users of this validation test case
    ------------------------------------------------
    Provide validation logic in __call__.
    Mark all measurements, or any other data, required from the
    model by decorator '@adaptermethod'."""

    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)
    @adaptermethod
    def get_addition(adapter, model, x, y):
        """get addition of x and y"""
        pass

    @adaptermethod
    def get_subtraction(adapter, model, x, y):
        """get difference of x and y"""
        pass

    def __call__(self, model, other_validation_data=None):
        """Method that each ValidationTestCase must implement.
        Parameters
        ----------
        @model :: The model that needs to be validated (not adapted model).
        The model adapter provided in the definition of this test case will
        be used internally to define an interface. The user of this validation
        test case will have to implement the resulting adapter interface."""

        d = other_validation_data if other_validation_data\
            else self.validation_data

        addition_measurement\
            = self.adapter.get_addition(model, d.x, d.y)
        subtraction_measurement\
            = self.adapter.get_subtraction(model, d.x, d.y)

        return ('PASS' if (all(addition_measurement == d.z) and
                           all(subtraction_measurement == d.w))
                else 'FAIL')


