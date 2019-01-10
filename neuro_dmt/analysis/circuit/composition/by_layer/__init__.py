"""Analysis of a circuit's composition, by layer."""

from abc import abstractmethod
from dmt.analysis import OfSinglePhenomenon
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import  Field, document_fields
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.analysis.circuit.composition import SpatialCompositionAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.report\
    import AnalysisReport


@document_fields
class ByLayerCompositionAnalysis(
        OfSinglePhenomenon,
        SpatialCompositionAnalysis):
    """..."""
    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            *args, **kwargs)

    def get_label(self, model):
        """Get a label for the circuit model. Will be useful in reporting"""
        return self.adapter.get_label(model)

    @property
    def plotting_parameter(self):
        """Implement this method if your Analysis plots data"""
        raise NotImplementedError(
            "Please provide this method to make your plots.")
    
    def add_plot_customization(self,
            model_measurement, **kwargs):
        """..."""
        try:
            kwargs['output_dir_path']\
                = self.output_dir_path
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "Could not find an attribute",
                "\tAttributeError: {}".format(e))

        kwargs.update(dict(
            title = name,
            xlabel = model_measurement.parameter,
            ylabel = "{} / [{}]".format(
                "mean {}".format(name.lower()),
                model_measurement.units) ))
        kwargs.update(self.plot_customization)

        return kwargs

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Plot the data.
        This a default method --- a subclass may have special needs to plot.
        In that case this method can be overridden."""
        data_record\
            = Record(
                data=model_measurement.data,
                label=model_measurement.label)

        return self.plotter_type(data_record)\
                  .with_customization(
                      self.add_plot_customization(
                          model_measurement,
                          **kwargs))\
                  .plot()

    def get_report(self, model_measurement):
        """Create a report."""
        figure = self.plot(model_measurement)
        return ValidationReport(
            phenomenon=self.phenomenon,
            author=self.author,
            caption=self.get_caption(model_measurement),
            figure=figure)

    @property
    def spatial_parameter_group(self):
        """..."""
        return ParameterGroup(tuple(self.spatial_parameters))


from neuro_dmt.analysis.circuit.composition.by_layer.\
    cell_density import CellDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.\
    cell_ratio import CellRatioAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.\
    synapse_density import SynapseDensityAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer.\
    soma_volume_fraction import SomaVolumeFractionAnalysis
