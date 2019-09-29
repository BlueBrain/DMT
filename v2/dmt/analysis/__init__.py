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
    """

    def __init__(self, *analyses):
        """
        Define an analysis suite as a list of analyses.
        """
        self._analyses = {
            analysis.phenomenon.label: analysis
            for analysis in analyses}

    @property
    def analyses(self):
        """
        Get analyses
        """
        return self._analyses

    def __call__(self, circuit_model,
            *args, **kwargs):
        """
        ...Call Me...
        """
        return {
            phenomenon.label: analysis(circuit_model, *args, **kwargs)
            for phenomenon, analysis in self._analyses.items()}
