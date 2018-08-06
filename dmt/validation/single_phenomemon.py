"""Code for validation test cases that analyze only one phenomenon."""
from abc import abstractmethod
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.utils.descriptor import Field

class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.

    Attributes
    ----------------------------------------------------------------------------
    validated_phenomenon :: Phenomenon #implemented as a Field(Phenomenon)
    """
    validated_phenomenon = Field(Phenomenon)

    def __init__(self, *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        if 'validated_phenomenon' in kwargs:
            self.validated_phenomenon = kwargs['validated_phenomenon']
        
        super(SinglePhenomenonValidation, self).__init__(*args, **kwargs)


    @abstractmethod
    def plot(self, *args, **kwargs):
        """Plot the data """
        pass

    @abstractmethod
    def get_caption(self):
        """Get caption that will be shown below the validation plot.

        Implementation Notes
        ------------------------------------------------------------------------
        Measurement method must be known to produce an informative caption.
        However this information is available only to the model adapter, and
        not to the class representing the validation itself. The author of
        the concrete implementation of SinglePhenomenonValidation will have to
        determine where to get the information required to produce a caption. 
        """
        pass
