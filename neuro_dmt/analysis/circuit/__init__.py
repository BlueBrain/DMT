"""Brain Circuit Analysis"""

import os
from dmt.analysis\
    import Analysis
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.measurement.parameter\
    import Parameter
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
    measurement_parameters=\
        Field(
            __name__="measurement_parameters",
            __typecheck__=Field.typecheck.collection(Parameter),
            __doc__="""Parameters used to measure the phenomenon""")
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """Create a {} with report type {}"""\
            .format(
                self.__class__.__name__,
                kwargs["ReportType"]))
        super().__init__(
            *args, **kwargs)

    def _get_output_dir(self,
            model_measurement=None,
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """Get output directory from kwargs {}""".format(kwargs),
            "and for model measurement {}".format(model_measurement))
        brain_region=\
            model_measurement.brain_region\
            if model_measurement and hasattr(model_measurement, "brain_region")\
               else self.brain_region
        return\
            os.path.join(
                super()._get_output_dir(),
                self.animal,
                brain_region.label)

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

    def get_measurement_parameters(self):
        """For an analysis this will be self.measurement_parameters.
        For a validation this will depend on the validation data."""
        return self.measurement_parameters

    def _for_given_parameter_values(self,
            **kwargs):
        return {
            parameter.label: kwargs[parameter.label]
            for parameter in self.measurement_parameters
            if (parameter.label not in self.plotted_parameters
                and parameter.label in kwargs)}

    def _get_plotting_parameter_label(self):
        """..."""
        if len(self.plotted_parameters):
            return self.plotted_parameters[0]
        return "X"


    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Plot the data.
        This a default method --- a subclass may have special needs to plot.
        In that case this method can be overridden.

        Note
        -----------
        Assuming that this Analysis will be for a single-phenomenon,
        we used 'model_measurement.phenomenon' to determine what will
        be plotted along the y-axis.
        """
        return self\
            .Plotter(
                model_measurement)\
            .plotting(
                model_measurement.phenomenon.label)\
            .versus(
                self._get_plotting_parameter_label())\
            .given(
                **self._for_given_parameter_values(
                    **kwargs))\
            .with_customization(
                **kwargs)\
            .plot()

    def get_report(self,
            model_measurement,
            *args, **kwargs):
        """Create a report.
        A default method is provided here."""
        try:
            figure=\
                self.plot(
                    model_measurement,
                    *args, **kwargs)
        except AttributeError as attribute_error:
            self.logger.alert(
                self.logger.get_source_info(),
                """{} instance  could not plot"""\
                .format(self.__class__.__name__),
                """Error caught: {}"""\
                .format(attribute_error))
            return\
                self.ReportType(
                    model_measurement=model_measurement.data,
                    phenomenon=self.phenomenon,
                    author=self.author,
                    caption=self.get_caption(
                        model_measurement,
                        **self._for_given_parameter_values(
                        **kwargs)))

        return\
            self.ReportType(
                model_measurement=model_measurement.data,
                phenomenon=self.phenomenon,
                author=self.author,
                figure=figure,
                caption=self.get_caption(
                    model_measurement,
                    **self._for_given_parameter_values(
                        **kwargs)))

