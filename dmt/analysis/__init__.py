"""Base classes for analyses."""

from abc import ABC, abstractmethod
from dmt.aii import Callable, AIBase
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.logging import Logger, with_logging

@document_fields
class AnalysisBaseClass(Callable, WithFCA):
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

        super().__init__(*args, **kwargs)

    @abstractmethod
    def __call__(self, model, *args, **kwargs):
        """An Analysis is a callable.
        In the concrete Analysis implementation,
        the first argument must be the model to be analyzed,
        and args and kwargs may contain relevant parameters."""
        pass



@with_logging(Logger.level.STUDY)
class Analysis(AnalysisBaseClass, AIBase):
    """"Just a class that mixes two.
    AnalysisBaseClass is useful by itself. Mixing in AIBase
     will add adapter interface goodies."""

    def __init__(self, *args, **kwargs):
        """..."""
        self.logger.info("-------------------------------------")
        self.logger.info("Reporting from Analysis")
        self.logger.info("initialize {} instance with kwargs:"\
                         .format(self.__class__.__name__))
        for k, v in kwargs.items():
            self.logger.info("{}: {}".format(k, v))
        self.logger.info("-------------------------------------")

        super(Analysis, self).__init__(*args, **kwargs)







