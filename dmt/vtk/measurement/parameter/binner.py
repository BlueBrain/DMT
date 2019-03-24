"""A class to bin parameters."""
from abc\
    import ABC\
    ,      abstractmethod

class ParameterBinner(
        ABC):
    """..."""

    @abstractmethod
    def get_bins(self, values):
        """
        Arguments
        -----------
        values :: Either a scalar, or a collection (np.array)

        Return
        -----------
        Either a scalar, or a collection (np.array)."""
        pass
    
