"""Utilities for circuit composition by layer."""
import os
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
from dmt.vtk.plotting.bars import BarPlot
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.utils.brain_region import Layer


@document_fields
class ByLayerCompositionValidation(SpatialCompositionValidation,
                                   SinglePhenomenonValidation):
    """Validation of a single circuit composition phenomenon."""
    plotter_type = BarPlot
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
        super(ByLayerCompositionValidation, self)\
            .__init__(validation_data, *args, **kwargs)

    def data_description(self):
        """Describe the experimental data used for validation."""
        return self.validation_data[0].what
     
    def get_label(self, circuit_model):
        """Get a label for the circuit model. Will be useful in reporting."""
        model = self.adapted(circuit_model)
        return model.get_label(circuit_model)

    def get_report(self, model_measurement):
        """Create a report."""
        plot_dir, plot_name = self.plot(model_measurement,
                                        output_dir_path = self.output_dir_path,
                                        file_name = 'report.png')
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            validated_phenomenon = self.validated_phenomenon,
            validation_image_dir = ".", #keep image dir relative
            validation_image_name = plot_name,
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = {d.label: d for d in self.validation_data},
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval
        )
