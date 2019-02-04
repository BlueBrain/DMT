"""Analysis of a circuit's composition."""

import os
from dmt.vtk.utils.descriptor import Field, document_fields
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.measurement.parameter import BrainCircuitSpatialParameter


@document_fields
class SpatialCompositionAnalysis(
        BrainCircuitAnalysis):
    """Analyze a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated."""
    
    spatial_parameters=\
        Field(
            __name__ = "spatial_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitSpatialParameter),
            __doc__ = """A composition phenomenon must be measured as a 
            function of location in the brain --- spatial_parameters represent 
            these locations. For example, you may want cell density as a 
            function of 'CorticalLayer'.""")
    
    def __init__(self,
            *args, **kwargs):
        """This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below."""
#       self.spatial_parameters = kwargs["spatial_parameters"]
        #self.p_value_threshold = kwargs.get("p_value_threshold", 0.05)
            
        # self.plot_customization=\
        #     kwargs.get(
        #         "plot_customization", {})
        super().__init__(
            *args, **kwargs)
