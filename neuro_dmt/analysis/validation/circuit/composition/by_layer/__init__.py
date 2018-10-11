"""Utilities for circuit composition by layer.
Validations defined here, (module 'by_layer') apply to any brain region
that has layers."""

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
from neuro_dmt.analysis.validation.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.analysis.validation.circuit.composition\
    import SpatialCompositionAnalysis
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

    implementations = {}

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below."""
        self.logger.debug(
            self.logger.get_source_info(),
            "initialize ByLayerCompositionValidation with kwargs",
            *["\t{}: {}".format(k, v) for k, v in kwargs.items()])
        super().__init__(
            phenomenon,
            *args, **kwargs)

    def get_label(self, model):
        """Get a label for the circuit model. Will be useful in reporting."""
        return self.adapter.get_label(model)

    @property
    @abstractmethod
    def plotting_parameter(self):
        """which parameter to plot against?"""
        pass

    def plot(self,
        model_measurement,
        comparison_label="dataset",
        *args, **kwargs):
        """Plot the data.
        This a default method --- a subclass may have special needs to plot.
        In that case this method can be overridden."""
        name\
            = model_measurement.phenomenon.name
        try:
            kwargs['output_dir_path']\
                = self.output_dir_path
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "Could not find an attribute",
                "\tAttributeError: {}".format(e))

        kwargs['title']\
            = name
        kwargs['xlabel']\
            = model_measurement.parameter
        kwargs['ylabel']\
            = "{} / [{}]".format(
                "mean {}".format(name.lower()),
                model_measurement.units)
        kwargs.update(self.plot_customization)
        data_record\
            = Record(
                data=model_measurement.data,
                label=model_measurement.label)
        plotter\
            = self.plotter_type(data_record)\
                  .comparing(comparison_label)\
                  .against(self.validation_data)\
                  .for_given(self.plotting_parameter)\
                  .with_customization(**kwargs)

        return plotter.plot()
            
    def get_report(self, model_measurement):
        """Create a report."""
        figure = self.plot(model_measurement)
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            phenomenon=self.phenomenon,
            author=self.author,
            caption=self.get_caption(model_measurement),
            reference_datasets=self.reference_datasets,
            is_pass=verdict == Verdict.PASS,
            is_fail=verdict == Verdict.FAIL,
            pvalue=pval,
            figure=figure)

    @property
    def spatial_parameter_group(self):
        """..."""
        return ParameterGroup(tuple(self.spatial_parameters))


from neuro_dmt.analysis.validation.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.analysis.validation.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.analysis.validation.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.analysis.validation.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation
from neuro_dmt.analysis.validation.circuit.composition.by_layer.\
    soma_volume_fraction import SomaVolumeFractionValidation
