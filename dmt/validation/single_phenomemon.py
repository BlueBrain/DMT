"""Code for validation test cases that analyze only one phenomenon."""
from abc import abstractmethod
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.utils.descriptor import Field, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.
    """
    validated_phenomenon = Field(
        __name__ = "validated_phenomenon",
        __type__ = Phenomenon,
        __doc__  = "The phenomenon that is measured for this validation."
    )
    def __init__(self, *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        super(SinglePhenomenonValidation, self).__init__(*args, **kwargs)
        if 'validated_phenomenon' in kwargs:
            self.validated_phenomenon = kwargs['validated_phenomenon']

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
