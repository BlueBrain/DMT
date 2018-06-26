"""A phenomenon is anything that manifests itself,
an observable fact or event. A phenomenon may be described by a system of
information related to matter, energy, or spacetimean"""

from abc import ABC, @abstractmethod

class Phenomenon(ABC):
    """Phenomenon is an observable fact or event, that can be measured."""

    #def __init__(self, name, description):
    #    """create a phenomenon with a name and a description."""
    #    self._name = name
    #    self._description = description

    @property
    @abstractmethod
    def name(self) -> str:
        """name of this phenomenon."""
        return self._name

    @property
    @abstractmethod
    def label(self) -> str:
        """label that can be used as a header entry
        (column name in a data-frame)"""
        return '_'.join(self._name.lower().split())
    
    @property
    @abstractmethod
    def description(self) -> str:
        """A wordy description of the phenomenon,
        explaining how it may be evaulated!"""
        pass
