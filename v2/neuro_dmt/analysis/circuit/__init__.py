"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import os
import pandas        
from dmt.analysis import Analysis
from dmt.model.interface import Interface
from dmt.tk.field import Field, lazyproperty
from dmt.tk.reporting import Report, Reporter

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
    AdapterInterface  = Field(
        """
        The interface that will be used to get measurements for the circuit
        model to analyze.
        """)
    measurement_parameters = Field(
        """
        A collection of parameters to measure with.
        This object should have the following methods:
        ~   1. `for_sampling`, returning an iterable of dict like parameters
        ~       to pass to a measurement method as keyword arguments.
        ~   2. `index`, returning a pandas.Index object to be used as an
        ~       index on the measurement.
        """)
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
        __default_value__=Reporter(
            path_output_folder=os.getcwd()))
    reference_data = Field(
        """
        A pandas.DataFrame containing reference data to compare with the
        measurement made on a circuit model.
        """,
        __required__=False)

    @lazyproperty
    def adapter_method(self):
        """
        Makes sense for analysis of a single phenomenon.
        """
        measurement_name = self\
            .AdapterInterface.__measurement__
        try:
            return getattr(self.adapter, measurement_name)
        except AttributeError:
            return getattr(self.adapter, "get_{}".format(measurement_name))

    def get_measurement(self,
            circuit_model,
            **measurement_parameters):
        """
        ...
        """
        return self.adapter_method(
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
                    self.get_measurement( circuit_model, **params )
                    for params in self.measurement_parameters.for_sampling]},
                index=self.measurement_parameters.index)

    def get_figures(self,
            circuit_model=None,
            measurement=None,
            *args, **kwargs):
        """
        Get a figure for the analysis of `circuit_model`.

        Arguments
        ----------
        `circuit_model`: A circuit model.
        `measurement`: The data frame to make a figure for.

        Either a `circuit_model` or a `measurement` must be provided.
        """
        measurement = measurement\
            if measurement is not None else\
               self._get_statistical_measurement(
                   circuit_model,
                   *args, **kwargs)
        return {
            self.phenomenon.label: self.plotter.get_figure(
                measurement.reset_index(),
                caption=self.adapter_method.__doc__)}

    def get_report(self,
            circuit_model,
            *args, **kwargs):
        """
        Get a report for the given `circuit_model`.
        """
        return Report(
            figures= self.get_figures(circuit_model=circuit_model),
            introduction="{}, measured by layer\n{}.".format(
                self.phenomenon.name,
                self.phenomenon.description),
            methods=self.adapter_method.__doc__,
            results="Results are presented in the figure.",
            discussion="To be provided after a review of the results")

    def __call__(self,
            circuit_model,
            adapter=None,
            *args, **kwargs):
        """
        Make this `Analysis` masquerade as a function.
        """
        if adapter is not None:
            self.adapter = adapter
        return self\
            .reporter\
            .post(
                self.get_report(
                    circuit_model,
                    *args, **kwargs))
