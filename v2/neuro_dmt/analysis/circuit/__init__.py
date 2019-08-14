"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import os
import pandas        
from dmt.analysis import Analysis
from dmt.model.interface import Interface
from dmt.tk.field import Field, lazyproperty
from dmt.tk.reporting import Reporter

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
        __default_value__=Reporter(
            path_output_folder=os.getcwd()))

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
                    self.get_measurement( circuit_model, **parameters )
                    for _ in range(self.sample_size)
                    for _, parameters in self.measurement_parameters.iterrows()]},
                index=self.measurement_index)

    def get_figure(self,
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
        return self.plotter\
            .get_figure(
                measurement.reset_index(),
                caption=self.adapter_method.__doc__)

    @abstractmethod
    def get_report(self,
            circuit_model,
            *args, **kwargs):
        """
        Prepare a report for this analysis of `circuit_model`.
        """
        raise NotImplementedError

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
