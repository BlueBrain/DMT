"""Utilities for circuit composition by layer."""
from abc import abstractmethod
import os
import pandas as pd
from dmt.data.reference import MultiReferenceData
from dmt.vtk.utils.descriptor import Field
from dmt.analysis.validation.test_case import SinglePhenomenonValidation
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import  document_fields
from dmt.vtk.utils.exceptions import ValueNotSetError
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.validations.circuit.composition import SpatialCompositionAnalysis
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.measurement.parameter\
    import LayerIndex, CorticalLayer, HippocampalLayer
    

@document_fields
class ByLayerCompositionValidation(
        SinglePhenomenonValidation,
        SpatialCompositionAnalysis):
    """Validation of a single circuit composition phenomenon.
    Validation is against reference data that provide experimental data
    as a function of layer. This base class may be used for validation
    composition of any brain region that is composed of layers."""

    reference_data = Field(
        __name__="reference_data",
        __type__=MultiReferenceData,
        __doc__="If not provided, assume validation does not use reference data")

    spatial_parameter = Field(
        __name__="spatial_parameter",
        __type__=LayerIndex,
        __doc__="This is a single spatial parameter validation.",
        __examples__=[CorticalLayer, HippocampalLayer])

    spatial_parameters = Field(
        __name__ = "spatial_parameters",
        __type__=set,
        __typecheck__ = Field.typecheck.collection(LayerIndex),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- spatial_parameters represent these
        locations. For example, you may want cell density as a function of
        'CorticalLayer'.""")

    implementations = {}

    def __init__(self, spatial_parameter, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below."""
        self.spatial_parameter = spatial_parameter
        self.spatial_parameters = {spatial_parameter}
        super().__init__(*args, **kwargs)

    def get_label(self, model):
        """Get a label for the circuit model. Will be useful in reporting."""
        return self.adapter.get_label(model)

    def get_report(self, model_measurement):
        """Create a report."""
        plot_dir, plot_name = self.plot(model_measurement,
                                        output_dir_path = self.output_dir_path,
                                        file_name = 'report.png')
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            validated_phenomenon = self.phenomenon,
            validation_image_dir = ".", #keep image dir relative
            validation_image_name = plot_name,
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_datasets,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval)

    @property
    def spatial_parameter_group(self):
        """..."""
        return ParameterGroup(tuple(self.spatial_parameters))

    @property
    def plotting_parameter(self):
        """This is a hack."""
        return self.spatial_parameter

from neuro_dmt.validations.circuit.composition.by_layer.cell_density \
    import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.cell_ratio \
    import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.inhibitory_synapse_density \
    import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.synapse_density \
    import SynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.soma_volume_fraction \
    import SomaVolumeFractionValidation
