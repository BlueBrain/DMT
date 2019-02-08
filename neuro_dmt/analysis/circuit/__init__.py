"""Brain Circuit Analysis"""

import os
from dmt.analysis\
    import Analysis
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.descriptor\
    import Field, WithFCA
from dmt.vtk.reporting\
    import Report
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.utils.brain_regions\
    import BrainRegion

class BrainCircuitAnalysis(
        Analysis):
    """Base class for a brain circuit analysis."""

    brain_region=\
        Field(
            __name__="brain_region",
            __type__=BrainRegion,
            __default__=brain_regions.whole_brain,
            __doc__="Provides a model independent tag for the brain region.")
    animal=\
        Field(
            __name__="animal",
            __type__=str,
            __doc__="""Animal for which the circuit was built. This will help
            organize reporting.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        #self.brain_region = kwargs["brain_region"]
        super().__init__(
            *args, **kwargs)

    def _get_output_dir(self):
        """..."""
        return\
            os.path.join(
                super()._get_output_dir(),
                self.animal,
                self.brain_region.label)

    @property
    def plotting_parameter(self):
        """Implement this method if your Analysis plots data"""
        raise NotImplementedError(
            "Please provide this method to make your plots.")
    
    def get_label(self, model):
        """Get a label for the circuit model. Will be useful in reporting"""
        return self.adapter.get_label(model)

    def add_plot_customization(self,
            model_measurement,
            *args, **kwargs):
        """This is a default method to add customization
        for a provided model measurement. It applies to data that
        are singly indexed, and cannot be used for plots that use
        multiply indexed data such as a heatmap."""
        try:
            kwargs['output_dir_path']= \
                self.output_dir_path
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                "Could not find an attribute",
                "\tAttributeError: {}".format(e))
        name=\
            model_measurement.phenomenon.name
        kwargs.update(
            dict(
                title = "{} {}".format(
                    model_measurement.label,
                    name),
                xlabel = model_measurement.parameter,
                ylabel = "{} / [{}]".format(
                    "mean {}".format(name.lower()),
                    model_measurement.units) ))
        kwargs.update(
            self.plot_customization)
        return kwargs

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Plot the data.
        This a default method --- a subclass may have special needs to plot.
        In that case this method can be overridden."""
        return\
            self.Plotter(
                model_measurement)\
                .with_customization(
                    self.add_plot_customization(
                        model_measurement,
                        **kwargs))\
                .plot()

    def get_report(self,
            model_measurement):
        """Create a report.
        A default method is provided here."""
        figure=\
            self.plot(
                model_measurement)
        return\
            self.ReportType(
                phenomenon=self.phenomenon,
                author=self.author,
                figure=figure,
                caption=self.get_caption(model_measurement))

