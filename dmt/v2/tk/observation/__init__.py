"""
Prototypes and documentation to help us develop Observation
"""

from abc import\
    abstractmethod
from ..field import\
    Field,\
    ClassAttribute,\
    WithFields

from ..quantity import Quantity

class Observation(WithFields):
    """
    Observation of a phenomenon.

    We model an Observation as a callable.
    We expect the measured system to be complex,
    whose description requires several dimensions.
    For example, a model of a brain circuit's properties can be observed as 
    functions of spatial variables X, Y, and Z, or as functions of biologically
    meaningful variables such as brain-regions, cortical layers
    and columns. Such spatial properties include cell density,
    synapse densities, and firing rates. In addition to spatial parameters,
    we may want to add synapse-class to the set of parameters conditioning the
    measurement. Such a measurement would have a separate entry for
    inhibitory and excitatory neurons for each combination of the
    spatial variables.
    """
    phenomenon = Field(
        """
        Phenomenon observed.
        """)
    result = Field(
        """
        Data resulting from this observation.
        """)
    parameters = Field(
        """
        A set of strings or a Parameter class that parameterize
        this observation / measurement.
        """)
    method = Field(
        """
        Description of the how this observation / measurement was made.
        """)
    @abstractmethod
    def __call__(**params):
        """
        Result of this measurement for the parameters in the
        keyword arguments 'params'.

        Arguments
        ----------
        params :: keyword arguments containing each parameter in
        'Field parameters' as a keyword.
        """
        pass


class Measurement(Observation):
    """
    Measurement is an Observation whose result is quantitative, 
    which means that it can be measured as a number.
    """
    pass
    
    
