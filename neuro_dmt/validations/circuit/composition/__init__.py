"""Code relevant for validation of composition phenomena"""

from abc import abstractmethod
from dmt.validation.test_case import SinglePhenomenonValidation
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils.brain_region import BrainRegion
from dmt.vtk.utils.descriptor import ClassAttribute, Field, document_fields
from dmt.vtk.utils.collections import Record

@document_fields
class SpatialCompositionValidation(SinglePhenomenonValidation):
    """Validates a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated.
    """
    region_type = ClassAttribute(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_value__ = lambda rtype: issubclass(rtype, BrainRegion),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- region type is the type of these
        location. For example, you may want cell density as a function of
        CorticalLayer."""
    )
    def __init__(self, validation_data, *args, **kwargs):
       """This validation will be made against multiple datasets. Each dataset
       should provide a 'Record' as specified below.

       Arguments
       -------------------------------------------------------------------------
       validation_data :: List[Record(measurement_label :: String,
       ~                              region_label :: String,
       ~                              data :: DataFrame["region", "mean", "std"])],
       ~                              citation :: Citation,
       ~                              what :: String)]
       -------------------------------------------------------------------------

       Keyword Arguments
       -------------------------------------------------------------------------
       p_value_threshold :: Float #optional
       output_dir_path :: String #optional
       report_file_name :: String #optional
       plot_customization :: Dict #optional
       """
       kwargs.update({'validation_data': validation_data})
       super(SpatialCompositionValidation, self).__init__(*args, **kwargs)

       self.p_value_threshold = kwargs.get('p_value_threshold', 0.05)
       self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
       self.report_file_name = kwargs.get('report_file_name', 'report.html')
       self.plot_customization = kwargs.get('plot_customization')

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


