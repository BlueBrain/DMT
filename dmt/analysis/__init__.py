# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Base classes for analyses
"""

from abc import abstractmethod
import os
import functools
from abc import ABC, abstractmethod
from dmt.tk.parameters import Parameters
from ..model import AIBase
from ..tk.field import Field, WithFields

class Analysis(WithFields, AIBase):
    """
    A base class that mixes in auto initialized Fields (using WithFields)
    and Adapter/Interface facility via AIBase.
    Users can base their classes on Analysis...
    """
        
    def __init__(self, *args, **kwargs):
        """
        We expect the user to initialize in their subclasses,
        or use fields3.
        """
        super().__init__(*args, **kwargs)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Every analysis should be a callable.
        """
        raise NotImplementedError


class Suite(WithFields):
    """
    A suite of analyses.

    An analysis suite should be used where it makes sense.
    For example, a suite of validation analyses is appropriate for a new
    circuit build. This suite will measure phenomena such as cell densities,
    inhibitory cell reations, synapse densities, etc.  We might want to analysze
    cell densities by depths instead of layers, or for each mtype. 
    """
    def __init__(self,
            *analyses,
            get_label=lambda analysis: analysis.label):
        """
        Define an analysis suite as a list of analyses.

        Arguments
        ----------------
        analyses: A sequence of analyses to constitute this suite of analyses.
        get_label: A call-back function to get label for an analysis.
        """
        self._analyses = {
            get_label(analysis): analysis
            for analysis in analyses}

    @property
    def analyses(self):
        """
        Get analyses
        """
        return self._analyses

    def __iter__(self):
        """
        Iterate through the analyses.
        """
        return (analysis for analysis in self._analyses.values())

    def __len__(self):
        """
        Size of this suite.
        """
        return len(self._analyses)

    def __call__(self, circuit_model,
            *args, **kwargs):
        """
        ...Call Me...
        """
        return {
            label: analysis(circuit_model, *args, **kwargs)
            for label, analysis in self._analyses.items()}

from .structured import StructuredAnalysis


def _adapted(method):
    """
    Wrap a method defined in an `Adapted` subclass
    such that it can be called with `adapter` as the first argument.
    """
    @functools.wraps(method)
    def wrapped(adapter, model, **kwargs):
        """
        Wrapped methodthod that will be used.
        """
        return method(model, **kwargs)
    return wrapped


class Adapted(ABC):
    """
    A mixin to define an analysis that has been adapted...
    """
    def __init__(self, adapter, *args, **kwargs):
        """..."""
        kwargs.update({
            "adapter": adapter,
            "measurement_parameters": _adapted(self.get_parameter_sets),
            "sample_measurement": _adapted(self.get_measurement),
            "figures": self.get_figures})
        super().__init__(*args, **kwargs)

    def __getattr__(self, method):
        """
        Delegate method to the adapter.
        """
        try:
            AdapterInterface = self.AdapterInterface
        except AttributeError:
            raise AttributeError(
                """
                {} has no such attribute: {}
                """.format(self, method))
                    
        if method in dir(AdapterInterface):
            try:
                return getattr(self._adapter, method)
            except AttributeError:
                pass
        raise AttributeError(
            """
            Attribute {} not available on {} or it's adapter {}.
            """.format(method, self, self._adapter))

    @abstractmethod
    def get_parameter_sets(self, model, *args, **kwargs):
        """
        Get measurement parameters.
        This method should expect at least two 
        """
        raise NotImplementedError

    @abstractmethod
    def get_measurement(self, model, **parameters):
        """
        Get measurement for a single set of parameters.

        Arguments
        ---------------
        parameters :: key-word arguments carrying all the parameter names and
        ~             values at which the measurement will be made.
        ~             Elements in these key-word arguments are expected to have 
        ~             been obtained from `self.measurement_parameters` or
        ~             been measurement specification that will be handled by 
        ~             the concrete implementation of this method.
        """
        raise NotImplementedError

    @abstractmethod
    def get_figures(self, measurement, *args, **kwargs):
        """
        A method that takes a measurement and some plotting specification,
        to produce figures!
        """
        raise NotImplementedError

    def __call__(self, circuit_model, **kwargs):
        """
        Run this analysis on a circuit.
        """
        #return self._runner(self.adapter, circuit_model, **kwargs)
        return super().__call__(self._adapter, circuit_model, **kwargs)
