"""Utilities for circuit composition by layer."""
from abc import abstractmethod
import pandas as pd
import numpy as np
from dmt.validation.test_case import SinglePhenomenonValidation
from neuro_dmt.validations.circuit.composition \
    import SpatialCompositionValidation
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, document_fields
from dmt.vtk.judgment.verdict import Verdict
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.utils.brain_region import Layer


@document_fields
class ByLayerCompositionValidation(SinglePhenomenonValidation,
                                   SpatialCompositionValidation):
    """Validation of a single circuit composition phenomenon."""
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

    def get_report(self, pval):
        """Create a report."""
        verdict = self.get_verdict(pval)
        return ValidationReport(
            validated_phenomenon = self.validated_phenomenon.title,
            validated_image_path = self.plot(model_measurement),
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_data,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval
        )
