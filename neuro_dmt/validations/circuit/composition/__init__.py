"""Code relevant for validation of composition phenomena"""

from dmt.validation.test_case import SinglePhenomenonValidation
from dmt.vtk.phenomenon import Phenomenonr
from neuro_dmt.utils.brain_region import BrainRegion
from dmt.vtk.utils.descriptor import Field, document_fields

@document_fields
class SpatialCompositionPhenomenonValidation(SinglePhenomenonValidation):
    """Validates a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated.
    """
    region_type = Field(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_value__ = lambda rtype: issubclass(rtype, BrainRegion),
        __doc_ = """A composition phenomenon must be measured as a function
        of location in the brain --- region type is the type of these
        location. For example, you may want cell density as a function of
        CorticalLayer."""
    )
    def __init__(self, validation_data, *args, **kwargs):
       """This validation will be made against multiple datasets. Each dataset
       should provide a 'Record' as specified below.
       """
       kwargs['validation_data'] = validation_data
       super(SpatialCompositionPhenomenonValidation, self)\
           .__init__(*args, **kwargs)

    @abstractmethod
    def plot(self, *args, **kwargs):
        """Plot the data."""
        pass

    @abstractmethod
    def get_caption(self):
        """Caption that will be shown below the validation plot.

        Implementation Notes
        ------------------------------------------------------------------------
        Measurement method must be known to produce an informative caption.
        However this information is available only to the model adapter, and
        not to the class representing the validation itself. The author of the
        concrete implementation of SinglePhenomenonValidation will have to
        determine where to get the information required to produce a caption.
        """
        pass


