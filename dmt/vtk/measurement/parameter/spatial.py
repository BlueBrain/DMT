"""Generic parameters to measure phenomena that are functions
of space."""

import numpy as np
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.measurement.parameter.binned\
    import BinnedParameter

class BinnedDistance(
        BinnedParameter):
    """Binned distance."""
    label = "distance"
    elem_type = float
    value_type = Field(
        __name__="value_type",
        __type__=tuple,
        __typecheck__=Field.typecheck.__tuple__(float, float),
        __doc__="""Bins containing floats can be defined as an interval.""")

    def __init__(self,
            lower_bound,
            upper_bound,
            number_bins=20,
            *args, **kwargs):
        """initialize the bins."""
        self.values=\
            []
        self.__number_bins=\
            number_bins
        self.__bin_width=\
            (upper_bound - lower_bounds) / number_bins
        self.values=[
            (lower_bound + i * self.__bin_width,
             lower_bound + (i + 1) * self.__bin_width)
            for i in range(number_bins)]
        self.value=\
            self.values[0]
        super().__init__(
            *args, **kwargs)

    def __contains__(self, value_x):
        """Does the current bin value contain the singleton value 'x'."""
        return\
            self.value[0] <= value_x\
            and value_x < self.value[1]

    def get_bin(self, value_x):
        """What bin value for 'x'?"""
        bin_index=\
            np.floor((value_x - self.values[0][0]) / self.__bin_width)
        if bin_index < 0 or bin_index >= self.__number_bins:
            raise OutOfRangeError(
                "value {} is out of binning range "\
                .format(
                    value_x,
                    self.values[0][0],
                    self.values[-1][1]))
        return\
            self.values[bin_index]
        
              


