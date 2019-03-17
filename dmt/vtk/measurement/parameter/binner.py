"""A class to bin parameters."""
from abc\
    import ABC\
    ,      abstractmethod

class ParameterBinner(
        ABC):
    """..."""

    @abstractmethod
    def get_bin(self, values):
        """
        Arguments
        -----------
        values :: Either a scalar, or a collection (np.array)

        Return
        -----------
        Either a scalar, or a collection (np.array)."""
        pass
    
