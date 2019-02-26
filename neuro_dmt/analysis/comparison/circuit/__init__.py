"""Comparison of circuit phenomena between two models,
or experiment and model."""

import pandas as pd
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.measurement.parameter\
    import Parameter
from dmt.vtk.plotting.comparison\
    import ComparisonPlot
from dmt.analysis.comparison\
    import Comparison
from neuro_dmt.analysis.comparison.report.single_phenomenon\
    import ComparisonReport


class CircuitPhenomenonComparison(
        Comparison):
    """Mixin to define comparison of a circuit phenomenon between
    a model and another model or experiment.
    """
    Plotter=\
        Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(ComparisonPlot),
            __doc__ = """A subclass of {} to compare results""".format(
                ComparisonPlot))

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

        if len(self.plotted_parameters) == 1:
            try:
                xvar= self.plotted_parameters[0]
                if isinstance(model_measurement.data.index, pd.MultiIndex):
                    assert\
                        xvar in model_measurement.data.index.names
            except AttributeError as aerr:
                self.logger.alert(
                    self.logger.get_source_info(),
                    "Missing attribute 'plotted_parameters'? {}".format(aerr))
                xvar= "not-available"
        else:
            xvar= "not-available"
        kwargs["ylabel"]=\
            "{} / [{}]".format(
                "mean {}".format(
                    phenomenon.name.lower()),
                model_measurement.units)
        kwargs.update(
            self.plot_customization)
        return self\
            .Plotter(
                model_measurement)\
            .against(
                self.reference_data_for_plotting,
                comparing=compared_quantity)\
            .plotting(
                phenomenon.label)\
            .versus(
                xvar)\
            .given(
                **self._for_given_parameter_values(
                    **kwargs))\
            .with_customization(
                **kwargs)\
            .plot()
    
    def get_report(self,
            model_measurement,
            *args, **kwargs):
        """..."""
        raise NotImplementedError()
