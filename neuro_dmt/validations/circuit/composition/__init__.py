"""Code relevant for validation of composition phenomena"""

from abc import abstractmethod
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.collections import Record
from dmt.vtk.judgment.verdict import Verdict
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.validations.circuit import BrainCircuitAnalysis
from neuro_dmt.measurement.parameter import BrainCircuitSpatialParameter


@document_fields
class SpatialCompositionAnalysis(
        BrainCircuitAnalysis):
    """Validates a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated."""
    
    spatial_parameters = Field(
        __name__ = "spatial_parameters",
        __type__=set,
        __typecheck__ = Field.typecheck.collection(BrainCircuitSpatialParameter),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- spatial_parameters represent these
        locations. For example, you may want cell density as a function of
        'CorticalLayer'.""")
       
    def __init__(self, *args, **kwargs): 
        """This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below."""
#       self.spatial_parameters = kwargs["spatial_parameters"]
        #self.p_value_threshold = kwargs.get("p_value_threshold", 0.05)
        #self.plotter_type = kwargs["plotter_type"]
        self.output_dir_path = kwargs.get("output_dir_path",
                                          os.path.join(os.getcwd(), "report"))
        self.report_file_name = kwargs.get("report_file_name", "report.html")
        self.plot_customization = kwargs.get("plot_customization", {})
        
        super().__init__(*args, **kwargs)
