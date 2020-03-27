# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Normal distribution
"""

from ....tk.field import Field, WithFields
import numpy as np

class Normal(WithFields):
    """
    Normal distribution
    """

    mean = Field("""
    Mean of the normal distribution.
    """,
       __type__=float)
    sigma = Field("""
    Standard deviation of the normal distribution.
    """,
        __type__=float)

    def random_variates(self, size=None):
        """Generate random variates.
        Arguments
        ----------
        size :: Either an int or a list of ints

        Return
        ----------
        If size is None, a single float
        If size is an int larger than 1, an array of 'size' floats
        If size is an array, an array of floats with shape the same as size
        """
        return np.random.normal(self.mean, self.sigma, size) if size\
            else np.random.normal(self.mean, self.sigma)

