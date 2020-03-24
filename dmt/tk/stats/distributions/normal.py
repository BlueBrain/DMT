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

