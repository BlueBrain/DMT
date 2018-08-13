"""We do not like the current way of specifying adapter methods."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.aii import AdapterInterfaceBase, Interface
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.author import Author

class IntegerMathTest(ValidationTestCase):
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

