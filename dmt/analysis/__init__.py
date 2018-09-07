"""Base classes for analyses."""

from abc import ABC, abstractmethod
from dmt.aii import Callable, AIBase
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import ClassAttribute, Field, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class AnalysisBaseClass(Callable):
    """Abstract Base Class for analysis of a model.

    Implementation Instructions
    ----------------------------------------------------------------------------
    Provide analysis logic in method '__call__'
    Mark all model measurements with decorator @abstractmethod.
    This will require the user of this Analysis to provide them for their model.
    """
    author = Field(
        __name__ = "author",
        __type__ = Author,
        __doc__  = """Author of this analysis."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        self.author = kwargs.get("author", Author.anonymous)

        super(AnalysisBaseClass, self).__init__(*args, **kwargs)

    @abstractmethod
    def __call__(self, model, *args, **kwargs):
        """An Analysis is a callable.
        In the concrete Analysis implementation,
        the first argument must be the model to be analyzed,
        and args and kwargs may contain relevant parameters."""
        pass

class Analysis(AnalysisBaseClass, AIBase):
    """"Just a class that mixes two.
    AnalysisBaseClass is useful by itself. Mixing in AIBase
     will add adapter interface goodies."""
    pass





