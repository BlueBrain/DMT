"""Code relevant for validation of composition phenomena"""

from abc import abstractmethod
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.collections import Record
from dmt.vtk.judgment.verdict import Verdict
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.validations.circuit import BrainCircuitAnalysis
from neuro_dmt.measurement.parameter import BrainCircuitSpatialParameter


@document_fields
class SpatialCompositionAnalysis(BrainCircuitAnalysis):
    """Validates a single composition phenomenon.
    This base-class provides the code common to all composition validations.
    Make your subclasses to implement 'abstractmethods' that depend on factors
    such the  region type used for measurements, and the phenomenon validated.
    """
    phenomenon = Field(
        __name__ = "analyzed_phenomenon",
        __type__ = Phenomenon,
        __doc__ = """Phenomenon analyzed, that can be used to create a
        report.""")
    
    plotter_type = Field(
        __name__="plotter_type",
        __typecheck__=Field.typecheck.subtype(ComparisonPlot),
        __doc__="""A subclass of {} to be used plot the results of
        this validation.""".format(ComparisonPlot))
    
    spatial_parameters = Field(
        __name__ = "spatial_parameters",
        __type__=set,
        __typecheck__ = Field.typecheck.collection(BrainCircuitSpatialParameter),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- spatial_parameters represent these
        locations. For example, you may want cell density as a function of
        'CorticalLayer'.""")
    

    output_dir_path = Field(
        __name__="output_dir_path",
        __type__=str,
        __default__=os.path.join(os.getcwd(), "report")
        __doc__="Where the report will be saved to.")

    report_file_name = Field(
        __name__="report_file_name",
        __type__=str,
        __default__="report.html",
        __doc__="By default, we assume that the report should be saved as an html."
    )

    _validations = {}

    @classmethod
    def add_validation(cls, v):
        """add validation"""
        f = v.phenomenon.label 
        if f not in cls._validations:
            cls._validations[f] = {}

        p = v.spatial_parameter_group.label
        if p not in cls._validations[f]:
            cls._validations[f][p] = v

        return cls._validations

    @classmethod
    def get_validation(cls, phenomenon, parameter):
        """..."""
        return cls._validations.get(phenomenon.label, {}).get(parameter.label, None)
        
    def __init__(self, *args, **kwargs): 
        """This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        -------------------------------------------------------------------------
        validation_data :: Either[
        ~   Record[data :: Dict[String -> MeasurementRecord], primary :: String],
        ~   Dict[String -> MeasurementRecord]
        ]
        where
        MeasurementRecord = List[Record(measurement_label :: String,
        ~                               region_label :: String,
        ~                               data :: DataFrame["mean", "std"])],
        ~                               citation :: Either[Citation, String],
        ~                               uri :: String,
        ~                               what :: String)]
        -------------------------------------------------------------------------
        
        Keyword Arguments
        -------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional
        report_file_name :: String #optional
        plot_customization :: Dict #optional
        """
#        self.spatial_parameters = kwargs["spatial_parameters"]
        #self.p_value_threshold = kwargs.get("p_value_threshold", 0.05)
        #self.output_dir_path = kwargs.get("output_dir_path",
        #                                  os.path.join(os.getcwd(), "report"))
        self.report_file_name = kwargs.get("report_file_name", "report.html")
        self.plotter_type = kwargs["plotter_type"]
        self.plot_customization = kwargs.get("plot_customization", {})
        
        self.add_validation(self)
        super().__init__(*args, **kwargs)
        

