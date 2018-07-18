"""Tools to handle stochastic observations, processes, etc."""

class Observation(object):
    """A statistical observation."""
    def __init__(self, mean=0.0, std=1.0, var=None):
        """You must pass one of standard deviation or variance.
        Parameters
        ----------
        @mean :: mean
        @std  :: standard deviation
        @var  :: variance.
        ----------------------------"""
        if (std is not None) and (var is not None) and (sqrt(var) != std):
            raise ValueError("""Variance != Sqrt(Stdev)!!!""")
        if (std is None) and (var is None):
            raise ValueError("""Provide at least one of Variance,
            or Standard Deviation!!!""")

        self._mean = mean
        self._std  = std if std is not None else sqrt(var)
        self._var  = std ** 2 if var is None else var

    @property
    def mean(self):
        """mean value"""
        return self._mean

    @proprety
    def std(self):
        """standard deviation value"""
        return self._std

    @property
    def var(self):
        """variance value"""
        return self._var

    def __sub__(self, other):
        """Subtract
        Parameters
        -----------
        @other :: Observation
        ---------------------"""
        return Observation(self.mean - other.mean,
                           sqrt(self.var + other.var))

    def __add__(self, other):
        """Add
        Parameters
        -----------
        @other :: Observation
        ---------------------"""
        return Observation(self.mean + other.mean,
                           sqrt(self.var + other.var))

    def __mul__(self, other):
        """Multiply
        Parameters
        -----------
        @other :: Observation
        ---------------------"""
        x = self.mean
        xvar = self.var
        y = other.mean
        yvar = other.var
        return Observation(mean=x**2 * y**2,
                           var=x**2 * yvar + xvar * y**2 + xvar * yvar)
                           

    def __truediv__(self, other):
        """Divide
        Parameters
        ----------
        @other :: Observation
        ---------------------"""
        return Observation(mean=x / y,
                           var=x**2 * yvar + xvar * y**2 + xvar * yvar)

