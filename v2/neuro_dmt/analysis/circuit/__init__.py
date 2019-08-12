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
        __type__=( pandas.Index, pandas.MultiIndex ))
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
        plot the results of this analysis.
        """,
        __required__=False)
    plotting_parameters = Field(
        """
        A dict listing the values of parameters that `plotter` will plot with.
        Having a list parameters allows plot customization to be placed in a
        single place, and applied to any suitable case.
        """,
        __default_value__={})
    reporter = Field(
        """
        A class or a module that will report the results of this analysis.
        It is up to the reporter what kind of report to generate. For example,
        the report can be a (interactive) webpage, or a static PDF.
        """,
        __required__=False)

    @abstractmethod
    def get_measurement(self,
            **measurement_parameters):
        """
        A subclass, or a mixin, must provide this method.
        """
        raise NotImplementedError

    def get_report(self,
            circuit_model,
            *args, **kwargs):
        """
        Get a report.
        """
        measurement = pandas\
            .DataFrame(
                {self.phenomenon.label: [
                    self.get_measurement( circuit_model, **parameters )
                    for _ in range(self.sample_size)
                    for parameters in self.measurement_parameters]},
                index=self.measurement_parameters)
        figure = self\
            .plotter\
            .plot(
                measurement.reset_index(),
                **plotting_parameters)
        return self\
            .reporter\
            .report(
                measurement,
                figure)

    pass



