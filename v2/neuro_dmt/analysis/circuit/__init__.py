"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import pandas        
from dmt.analysis import Analysis
from dmt.model.interface import Interface
from dmt.tk.field import Field, lazyproperty

class BrainCircuitAnalysis(
        Analysis):
    """
    A base class for all circuit analyses.
    """
    phenomenon = Field(
        """
        An object whose `.label` is a single word name for the phenomenon 
        analyzed by this `BrainCircuitAnalysis`.
        """)
    measurement_parameters = Field(
        """
        A collection of parameters to measure with.
        """,
        __type__=pandas.DataFrame)

    @lazyproperty
    def measurement_index(self):
        """
        The index to be given to the measurement.
        Each row in `measurement_parameters` is represented in `sample_size`
        number of times.
        """
        return pandas\
            .DataFrame(
                [parameters.to_dict()
                 for _ in range(self.sample_size)
                 for _, parameters in self.measurement_parameters.iterrows()])\
            .set_index(
                list(self.measurement_parameters.columns.values))\
                .index

    sample_size = Field(
        """
        Number of samples to collect for each measurement.
        """,
        __default_value__ = 20)
    AdapterInterface  = Field(
        """
        The interface that will be used to get measurements for the circuit
        model to analyze.
        """,
        __type__=Interface)
    plotter = Field(
        """
        A class or a module that has `plot` method that will be used to
        plot the results of this analysis. The plotter should know how to 
        interpret the data provided. For example, the plotter will have to know
        which columns are the x-axis, and which the y-axis. The `Plotter`
        instance used by this `BrainCircuitAnalysis` instance should have those
        set as instance attributes.
        """,
        __required__=False)
    reporter = Field(
        """
        A class or a module that will report the results of this analysis.
        It is up to the reporter what kind of report to generate. For example,
        the report can be a (interactive) webpage, or a static PDF.
        """,
        __required__=False)

    def get_measurement(self,
            circuit_model,
            **measurement_parameters):
        """
        ...
        """
        measurement_name = self\
            .AdapterInterface.__measurement__
        try:
            adapter_method = getattr(
                self.adapter,
                measurement_name)
        except AttributeError:
            adapter_method = getattr(
                self.adapter,
                "get_{}".format(measurement_name))

        return adapter_method(
            circuit_model,
            **measurement_parameters)

    def _get_statistical_measurement(self,
            circuit_model,
            *args, **kwargs):
        """
        Get a statistical measurement.
        """
        return pandas\
            .DataFrame(
                {self.phenomenon.label: [
                    self.get_measurement( circuit_model, **parameters )
                    for _ in range(self.sample_size)
                    for _, parameters in self.measurement_parameters.iterrows()]},
                index=self.measurement_index)

    def get_report(self,
            circuit_model,
            *args, **kwargs):
        """
        Get a report.
        """
        measurement = self\
            ._get_statistical_measurement(
                circuit_model,
                *args, **kwargs)
        figure = self\
            .plotter\
            .plot(
                measurement.reset_index())
        return self\
            .reporter\
            .report(
                measurement,
                figure)

    pass



