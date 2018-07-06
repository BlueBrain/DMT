"""A physical quantity consists of a magnitude and a unit.
It is the result of measuring a physical phenomenon,
and thus component of a measurement."""


from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from dmt.phenomenon import Phenomenon

class Quantity(ABC):
    """Quantity consists of a magnitude and a unit.
    We define Quantity to be abstract to accommodate different
    types of data-frames depending on what the quantity represents.

    Notes
    -----------
    A Quantity cannot be labeled --- both CellRatio and CellDensity are 
    measured by the same Quantity --- but are different phenomena.
    Quantity thus expresses the type of the phenomenon's measured numerical
    value along with the weight factor in the associated units."""

    def __init__(self, magnitude, unit):
        """
        Parameters
        ----------
        unit: MeasurementUnit
        magnitude: scalar, vector, or a data-frame.

        Notes
        ----------
        Statistical measurements should return a data-frame.
        We can suggest / enforce this by defining a class StatisticalQuantity"""

        self._magnitude = magnitude
        self._unit = unit

    @abstractmethod
    @property
    def magnitude(self):
        """The value of this quantity.
        Should be determined by self._magnitude."""
        pass

    @property
    def in_units(self, alt_units):
        """The same quantity in different units.
        Exact details of the conversion will depend on the type of
        the Quantity's magnitude. For example, consider a quantity representing
        cell density. Cell density in the cortex will have consist of 6 numbers
        per sample, while that in the hippocampus will consist of 4."""

        return self._unit.weight_per(alt_unit) * self._magnitude


class ScalarQuantity(Quantity):
    """Quantity whose magnitude is a single number."""

    @property
    def magnitude(self):
        """self._magnitude should be a scalar"""
        return self._magnitude


class VectorQuantity(Quantity):
    """Quantity whose magnitude is a named tuple of floats,
    or a pandas Series object."""

    @property
    def magnitude(self):
        """self._magnitude should be a tuple or a pandas Series object."""
        m = self._magnitude
        if isinstance(m, pd.core.series.Series):
            return m.copy()
        if isinstance(m, np.ndarray):
            return np.copy(m)
        if isinstance(m, tuple):
            return m

        import copy
        return copy.deepcopy(m)

class MatrixQuantity(Quantity):
    """Some physical quantities are matrices!
    We will use numpy arrays for magnitude.
    As e.g. the number of connections between pathways of a brain circuit."""

    @property
    def magnitude(self):
        """self._magnitude should be a np.array"""
        return np.copy(self._magnitude)

class StatisticalQuantity(Quantity):
    """A statistical quantity's magnitude will be a data-frame,
    or another iterable. All the columns of the data-frame should contain
    the same scalar quantity!

    Limitations
    ------------
    We have defined StatisticalQuantity as the statistical version of
    VectorQuantity. We could impose this requirement --- it should work fine
    for scalar quantities. However, we cannot accommodate MatrixQuantity's
    statistical extension.
    """

    @property
    def sample_size(self) -> int:
        return self._magnitude.shape[0]

    @property
    def magnitude(self):
        """self._magnitude should be a data-frame,
        so we return a copy."""
        return self._magnitude.copy()

    @property
    def mean(self):
        """Mean over the samples present in this Quantity."""
        return VectorQuantity(self._magnitude.mean(), self._unit)

    @property
    def std(self):
        """Standard deviation over the samples present in this Quantity."""
        return VectorQuantity(self._magnitude.std(), self._unit)

