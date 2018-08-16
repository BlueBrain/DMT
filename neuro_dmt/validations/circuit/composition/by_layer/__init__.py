"""Utilities for circuit composition by layer."""
from abc import abstractmethod
import pandas as pd
import numpy as np
from dmt.validation.test_case import SinglePhenomenonValidation
from neuro_dmt.validations.circuit.composition \
    import SpatialCompositionValidation
from neuro_dmt.validations.circuit.composition \
    import SpatialCompositionValidation
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, document_fields
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.utils.brain_region import Layer


@document_fields
class ByLayerCompositionValidation(SinglePhenomenonValidation,
                                   SpatialCompositionValidation):
    """Validation of a single circuit composition phenomenon."""
    region_type = Field(
        __name__ = "region_type",
        __type__ = type,
        __is_valid_value__ = lambda rtype: issubclass(rtype, Layer),
        __doc__ = """Composition phenomena are to measured as a function of
        a region type, for example cell density in the cortex as a function of
        'CorticalLayer' or 'HippocampalLayer'"""
    )
    def __init__(self, validation_data, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(measurement_label :: String,
        ~                              region_label :: String,
        ~                              data :: DataFrame["region", "mean", "std"])],
        ~                              citation :: Citation,
        ~                              what :: String)]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional
        report_file_name :: String #optional
        plot_customization :: Dict #optional
        """
        super(ByLayerCompositionValidation, self).__init__(*args, **kwargs)
        #we can add some 


    def get_label(self, circuit_model):
        """Get a label for the circuit model. Will be useful in reporting."""
        model = self.adapted(circuit_model)
        return model.get_label(circuit_model)
