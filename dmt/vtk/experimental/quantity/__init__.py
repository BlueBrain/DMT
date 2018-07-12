"""An experimental implementation of quantity"""

import copy
import pandas as pd
import numpy as np

class NumberLike:
    """to experiment"""

    def __init__(self, value):
        self.__value = value

    def __value__(self):
        """getter of value"""
        if (isinstance(self.__value, pd.core.series.Series) or
            isinstance(self.__value, pd.core.frame.DataFrame)):
            return self.__value.copy()
        if (isinstance(self.__value, np.ndarray) or
            isinstance(self.__value, np.matrixlib.defmatrix.matrix)):
            return np.copy(self.__value)

        return copy.deepcopy(self.__value)

    @classmethod
    def __accepts__(cls, x):
        """determine if the value x represents a magnitude"""
        return (
            hasattr(x, '__add__') and
            hasattr(x, '__sub__') and
            (hasattr(x, '__mul__') or hasattr(x, '__matmul__'))  and
            (hasattr(x, '__truediv__') or hasattr(x, '__div__') or
             hasattr(x, '__divmod__'), hasattr(x, '__floordiv__')) and
            hasattr(x, '__pow__')
        )


from dmt.experimental.descriptor import Field

class Quantity:
    """Quantity consists of a magnitude and a unit.
    The magnitude of a Quantity may be a number, a list of numbers,
    a matrix, or a data-frame. Magnitude can be anything on which
    basic math operators +, -, *, / can can work.
    Quantity thus expresses the type of a Phenomenon's measured numerical
    value along with the weight factor in the associated units."""

    magnitude = Field(NumberLike)
    #unit = Field(Unit)

    def __init__(self, magnitude):
        """
        Parameters
        ----------
        @magnitude :: a quantity that acts like a number
        @unit :: Unit"""

        self.magnitude = magnitude
        #self.unit = unit
