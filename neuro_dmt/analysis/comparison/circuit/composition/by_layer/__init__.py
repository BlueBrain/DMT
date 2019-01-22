"""Compare model phenomena by layer."""
from dmt.analysis.comparison\
    import Comparison
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field, document_fields
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis
from neuro_dmt.analysis.comparison.report.single_phenomenon\
    import ComparisonReport
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis,\
    CellDensityAnalysis,\
    CellRatioAnalysis,\
    InhibitorySynapseDensityAnalysis,\
    SynapseDensityAnalysis

@document_fields
class ByLayerCompositionComparison(
        Comparison):
    """..."""

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """...
        """
        super().__init__(
            phenomenon,
            *args, **kwargs)

    def plot(self,
            model_measurement,
            compared_quantity="dataset",
            *args, **kwargs):
        """Plot the comparison as a bars by layer.
        This is a default method --- a subclass may have special needs to plot.
        In that case this method can be overridden."""
        phenomenon=\
            model_measurement.phenomenon
        try:
            kwargs["output_dir_path"]=\
                self.output_dir_path
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "Could not find attribute 'output_dir_path'.",
                "\tAttributeError: {}".format(e))
        kwargs["title"]=\
            model_measurement.label
        kwargs["xlabel"]=\
            model_measurement.parameter
        kwargs["ylabel"]=\
            "{} / [{}]".format(
                "mean {}".format(phenomenon.name.lower()),
                model_measurement.units)
        kwargs.update(
            self.plot_customization)
        return\
            self.plotter_type(
                Record(
                    data=model_measurement.data,
                    label=model_measurement.label)
            ).comparing(
                    compared_quantity
            ).against(
                self.reference_data_for_plotting
            ).for_given(
                self.plotting_parameter
            ).with_customization(
                **kwargs
            ).plot()

    def get_report(self,
            model_measurement):
        """..."""
        figure=\
            self.plot(
                model_measurement)
        pval=\
            self.pvalue(
                model_measurement)
        verdict=\
            self.get_verdict(
                pval)
        return\
            ComparisonReport

class CellDensityComparison(
        ByLayerCompositionComparison,
        CellDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


class CellRatioComparison(
        ByLayerCompositionComparison,
        CellRatioAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


class InhibitorySynapseDensityComparison(
        ByLayerCompositionComparison,
        InhibitorySynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


class SynapseDensityComparison(
        ByLayerCompositionComparison,
        SynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
