"""
Base classes for analyses
"""

import os
from abc import ABC, abstractmethod
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
        or use fields.
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
            phenomenon.label: analysis(circuit_model, *args, **kwargs)
            for phenomenon, analysis in self._analyses.items()}
