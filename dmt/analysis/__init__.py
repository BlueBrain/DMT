"""Base classes for analyses."""

from abc import ABC, abstractmethod
from dmt.model import Callable, AIBase
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.logging import Logger, with_logging

@with_logging(Logger.level.STUDY)
@document_fields
class Analysis(WithFCA, AIBase):
    """"Just a class that mixes two.
    AnalysisBaseClass is useful by itself. Mixing in AIBase
     will add adapter interface goodies."""

    phenomena = Field(
        __name__="phenomenon",
        __typecheck__=Field.typecheck.collection(Phenomenon),
        __doc__="Phenomena analyzed."
    )
    author = Field(
        __name__="author",
        __type__=Author,
        __default__=Author.anonymous,
        __doc__="""Author of this analysis."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @abstractmethod
    def __call__(self, model, *args, **kwargs):
        """An Analysis is a callable.
        In the concrete Analysis implementation,
        the first argument must be the model to be analyzed,
        and args and kwargs may contain relevant parameters."""
        pass

